# -*- coding: utf-8 -*-
import glob
import os
import sys

import matplotlib

matplotlib.use("WXAgg")
from loguru import logger

# from gooey import Gooey, GooeyParser
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


@Gooey(
    program_name="Physio pipeline",
    program_description="Physiological processing pipeline",
    default_size=(800, 600),
    target=TARGET,
)
def get_parser():
    """Parser for GUI and command-line arguments"""
    parser = GooeyParser()
    parser.add_argument(
        "file_template",
        metavar="Filename template",
        widget="FileChooser",
        help="Select a representative file and replace all "
        'subject-specific information with a "?" symbol.'
        "\nFor example, subject_001_data.txt should "
        "become subject_???_data.txt and will expand to "
        "match\nsubject_001_data.txt, subject_002_data."
        "txt, ..., subject_999_data.txt.",
    )

    inp_group = parser.add_argument_group(
        "Inputs", "Options to specify " "format of input files"
    )
    inp_group.add_argument(
        "--modality",
        metavar="Modality",
        default="ECG",
        choices=list(MODALITIES.keys()),
        help="Modality of input data.",
    )
    inp_group.add_argument(
        "--fs",
        metavar="Sampling rate",
        default=1000.0,
        type=float,
        help="Sampling rate of input data.",
    )
    inp_group.add_argument(
        "--source",
        metavar="Source",
        default="rtpeaks",
        choices=list(LOADERS.keys()),
        help="Program used to collect the data.",
    )
    inp_group.add_argument(
        "--channel",
        metavar="Channel",
        default=1,
        type=int,
        help="Which channel of data to read from data "
        'files.\nOnly applies if "Source" is set to '
        "rtpeaks.",
    )

    out_group = parser.add_argument_group(
        "Outputs", "Options to specify " "format of output files"
    )
    out_group.add_argument(
        "-o",
        "--output",
        metavar="Filename",
        default="peakdet.csv",
        help="Output filename for generated measurements.",
    )
    out_group.add_argument(
        "-m",
        "--measurements",
        metavar="Measurements",
        nargs="+",
        widget="Listbox",
        choices=list(ATTR_CONV.keys()),
        default=["Average NN intervals", "Standard deviation of NN intervals"],
        help="Desired physiological measurements.\nChoose "
        "multiple with shift+click or ctrl+click.",
    )
    out_group.add_argument(
        "-s",
        "--savehistory",
        metavar="Save history",
        action="store_true",
        help="Whether to save history of data processing " "for each file.",
    )

    edit_group = parser.add_argument_group(
        "Workflow arguments (optional!)",
        "Options to specify modifications " "to workflow",
    )
    edit_group.add_argument(
        "-n",
        "--noedit",
        metavar="Editing",
        action="store_true",
        help="Turn off interactive editing.",
    )
    edit_group.add_argument(
        "-t",
        "--thresh",
        metavar="Threshold",
        default=0.2,
        type=float,
        help="Threshold for peak detection algorithm.",
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
    measurements=ATTR_CONV.keys(),
    verbose=False
):
    """
    Basic workflow for physiological data

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
    measurements : list, optional
        Which HRV-related measurements to save from data. See ``peakdet.HRV``
        for available measurements. Default: all available measurements.
    verbose : bool, optional
        Whether to include verbose logs when catching exceptions that include diagnostics
    """
    logger.remove(0)
    logger.add(sys.stderr, backtrace=verbose, diagnose=verbose)
    # output file
    logger.info("OUTPUT FILE:\t\t{}\n".format(output))
    # grab files from file template
    logger.info("FILE TEMPLATE:\t{}\n".format(file_template))
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
        with open(output, "r") as src:
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
            logger.info("Currently processing {}".format(fname))

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
    logger.enable("")
    opts = get_parser().parse_args()
    workflow(**vars(opts))


if __name__ == "__main__":
    main()
