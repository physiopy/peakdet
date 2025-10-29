"""Parser and physio workflow."""

import argparse
import datetime
import glob
import os
import sys

from loguru import logger

import peakdet

TARGET = "pythonw" if sys.platform == "darwin" else "python"
TARGET += " -u " + os.path.abspath(__file__)

LOADERS = dict(rtpeaks=peakdet.load_rtpeaks, MRI=peakdet.load_physio)

MODALITIES = dict(
    ECG=([5.0, 15.0], "bandpass"), PPG=(2, "lowpass"), RESP=([0.05, 0.5], "bandpass")
)

ATTR_CONV = {
    "Average NN intervals": "avgnn",
    "Root mean square of successive differences": "rmssd",
    "Standard deviation of NN intervals": "sdnn",
    "Standard deviation of successive differences": "sdsd",
    "Number of successive differences >50 ms": "nn50",
    "Percent of successive differences >50 ms": "pnn50",
    "Number of successive differences >20 ms": "nn20",
    "Percent of successive differences >20 ms": "pnn20",
    "High frequency HRV hfHRV": "hf",
    "Log of high frequency HRV, log(hfHRV)": "hf_log",
    "Low frequency HRV, lfHRV": "lf",
    "Log of low frequency HRV, log(lfHRV)": "lf_log",
    "Very low frequency HRV, vlfHRV": "vlf",
    "Log of very low frequency HRV, log(vlfHRV)": "vlf_log",
    "Ratio of lfHRV : hfHRV": "lftohf",
    "Peak frequency of hfHRV": "hf_peak",
    "Peak frequency of lfHRV": "lf_peak",
}


def get_parser():
    """Parser for GUI and command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_template",
        help="Select a representative file and replace all "
        'subject-specific information with a "?" symbol.'
        "\nFor example, subject_001_data.txt should "
        "become subject_???_data.txt and will expand to "
        "match\nsubject_001_data.txt, subject_002_data."
        "txt, ..., subject_999_data.txt.",
    )

    inp_group = parser.add_argument_group(
        "Inputs", "Options to specify format of input files"
    )
    inp_group.add_argument(
        "--modality",
        default="ECG",
        choices=list(MODALITIES.keys()),
        help="Modality of input data.",
    )
    inp_group.add_argument(
        "--fs",
        default=1000.0,
        type=float,
        help="Sampling rate of input data.",
    )
    inp_group.add_argument(
        "--source",
        default="rtpeaks",
        choices=list(LOADERS.keys()),
        help="Program used to collect the data.",
    )
    inp_group.add_argument(
        "--channel",
        default=1,
        type=int,
        help="Which channel of data to read from data "
        'files.\nOnly applies if "Source" is set to '
        "rtpeaks.",
    )

    out_group = parser.add_argument_group(
        "Outputs", "Options to specify format of output files"
    )
    out_group.add_argument(
        "-o",
        "--output",
        default="peakdet.csv",
        help="Output filename for generated measurements.",
    )
    out_group.add_argument(
        "-m",
        "--measurements",
        metavar="Measurements",
        nargs="+",
        choices=list(ATTR_CONV.keys()),
        default=["Average NN intervals", "Standard deviation of NN intervals"],
        help="Desired physiological measurements",
    )
    out_group.add_argument(
        "-s",
        "--savehistory",
        action="store_true",
        help="Whether to save history of data processing for each file.",
    )

    edit_group = parser.add_argument_group(
        "Workflow arguments (optional!)",
        "Options to specify modifications to workflow",
    )
    edit_group.add_argument(
        "-n",
        "--noedit",
        action="store_true",
        help="Turn off interactive editing.",
    )
    edit_group.add_argument(
        "-t",
        "--thresh",
        default=0.2,
        type=float,
        help="Threshold for peak detection algorithm.",
    )

    log_style_group = parser.add_argument_group(
        "Logging style arguments (optional and mutually exclusive)",
        "Options to specify the logging style",
    )
    log_style_group_exclusive = log_style_group.add_mutually_exclusive_group()
    log_style_group_exclusive.add_argument(
        "-debug",
        "--debug",
        dest="debug",
        action="store_true",
        help=(
            "Print additional debugging info and error diagnostics to log file. "
            "Default is False."
        ),
        default=False,
    )
    log_style_group_exclusive.add_argument(
        "-quiet",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Only print warnings to log file. Default is False.",
        default=False,
    )

    return parser


@logger.catch
def workflow(
    *,
    file_template,
    modality,
    fs,
    source="MRI",
    channel=1,
    output="peakdet.csv",
    savehistory=True,
    noedit=False,
    thresh=0.2,
    measurements=None,
    debug=False,
    quiet=False,
):
    """
    Run basic workflow for physiological data.

    Parameters
    ----------
    file_template : str
        Template filename for data inputs
    modality : {'ECG', 'PPG', 'RESP'}
        Currently support data modalities
    fs : float
        Sampling rate of input data
    source : {'rtpeaks', 'MRI'}, optional
        How data were acquired. Default: 'MRI'
    channel : int, optional
        Which channel of data to analyze; only applies if source is 'rtpeaks'.
        Default: 1
    output : str, optional
        Desired output filename. Default: 'peakdet.csv'
    savehistory : bool, optional
        Whether to save editing history of each file with
        ``peakdet.save_history``. History will be used if this workflow is
        run again on the samed data files. Default: True
    noedit : bool, optional
        Whether to disable interactive editing of physio data. Default: False
    thresh : [0, 1] float, optional
        Threshold for peak detection. Default: 0.2
    measurements : None or list, optional
        Which HRV-related measurements to save from data. See ``peakdet.HRV``
        for available measurements.
        Default: None, that is all available measurements.
    verbose : bool, optional
        Whether to include verbose logs when catching exceptions that include diagnostic
    """
    if measurements is None:
        measurements = ATTR_CONV.keys()
    outdir = os.path.dirname(output)
    logger.info(f"Current path is {outdir}")

    # Create logfile name
    basename = "peakdet"
    extension = "log"
    isotime = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
    logname = os.path.join(outdir, (basename + isotime + "." + extension))

    logger.remove(0)
    if quiet:
        logger.add(
            sys.stderr,
            level="WARNING",
            colorize=True,
            backtrace=False,
            diagnose=False,
        )
        logger.add(
            logname,
            level="WARNING",
            colorize=False,
            backtrace=False,
            diagnose=False,
        )
    elif debug:
        logger.add(
            sys.stderr,
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        logger.add(
            logname,
            level="DEBUG",
            colorize=False,
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            sys.stderr,
            level="INFO",
            colorize=True,
            backtrace=True,
            diagnose=False,
        )
        logger.add(
            logname,
            level="INFO",
            colorize=False,
            backtrace=True,
            diagnose=False,
        )

    # output file
    logger.info(f"OUTPUT FILE:\t\t{output}")
    # grab files from file template
    logger.info(f"FILE TEMPLATE:\t{file_template}")
    files = glob.glob(file_template, recursive=True)

    # convert measurements to peakdet.HRV attribute friendly names
    try:
        logger.info("REQUESTED MEASUREMENTS: {}\n".format(", ".join(measurements)))
    except TypeError:
        raise TypeError(
            "It looks like you didn't select any of the options "
            "specifying desired output measurements. Please "
            "select at least one measurement and try again."
        )
    measurements = [ATTR_CONV[attr] for attr in measurements]

    # get appropriate loader
    load_func = LOADERS[source]

    # check if output file exists -- if so, ensure headers will match
    head = "filename," + ",".join(measurements)
    if os.path.exists(output):
        with open(output) as src:
            eheader = src.readlines()[0]
        # if existing output file does not have same measurements are those
        # requested on command line, warn and use existing measurements so
        # as not to totally fork up existing file
        if eheader != head:
            logger.warning(
                "Desired output file already exists and requested "
                "measurements do not match with measurements in "
                "existing output file. Using the pre-existing "
                "measurements, instead."
            )
            measurements = [f.strip() for f in eheader.split(",")[1:]]
        head = ""
    # if output file doesn't exist, nbd
    else:
        head += "\n"

    with open(output, "a+") as dest:
        dest.write(head)
        # iterate through all files and do peak detection with manual editing
        for fname in files:
            fname = os.path.relpath(fname)
            logger.info(f"Currently processing {fname}")

            # if we want to save history, this is the output name it would take
            outname = os.path.join(
                os.path.dirname(fname), "." + os.path.basename(fname) + ".json"
            )

            # let's check if history already exists and load that file, if so
            if os.path.exists(outname):
                data = peakdet.load_history(outname)
            else:
                # load data with appropriate function, depending on source
                if source == "rtpeaks":
                    data = load_func(fname, fs=fs, channel=channel)
                else:
                    data = load_func(fname, fs=fs)

                # filter
                flims, method = MODALITIES[modality]
                data = peakdet.filter_physio(data, cutoffs=flims, method=method)

                # perform peak detection
                data = peakdet.peakfind_physio(data, thresh=thresh)

            # edit peaks, if desired (HIGHLY RECOMMENDED)
            # we'll do this even if we loaded from history
            # just to give another chance to check things over
            if not noedit:
                data = peakdet.edit_physio(data)

            # save back out to history, if desired
            if savehistory:
                peakdet.save_history(outname, data)

            # keep requested outputs
            hrv = peakdet.HRV(data)
            outputs = ["{:.5f}".format(getattr(hrv, attr, "")) for attr in measurements]

            # save as we go so that interruptions don't screw everything up
            dest.write(",".join([fname] + outputs) + "\n")


def main():
    """Run main entrypoint."""
    logger.enable("")
    opts = get_parser().parse_args()
    workflow(**vars(opts))


if __name__ == "__main__":
    """Run main entrypoint."""
    main()
