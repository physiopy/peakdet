# -*- coding: utf-8 -*-

import glob
import os
import warnings
from gooey import Gooey, GooeyParser
import peakdet

modalities = dict(ECG=peakdet.ECG,
                  PPG=peakdet.PPG,
                  RESP=peakdet.RESP)

attr_conv = {'Average NN intervals': 'avgnn',
             'Root mean square of successive differences': 'rmssd',
             'Standard deviation of NN intervals': 'sdnn',
             'Standard deviation of successive differences': 'sdsd',
             'Number of successive differences >50 ms': 'nn50',
             'Percent of successive differences >50 ms': 'pnn50',
             'Number of successive differences >20 ms': 'nn20',
             'Percent of successive differences >20 ms': 'pnn20',
             'High frequency HRV hfHRV': 'hf',
             'Log of high frequency HRV, log(hfHRV)': 'hf_log',
             'Low frequency HRV, lfHRV': 'lf',
             'Log of low frequency HRV, log(lfHRV)': 'lf_log',
             'Very low frequency HRV, vlfHRV': 'vlf',
             'Log of very low frequency HRV, log(vlfHRV)': 'vlf_log',
             'Ratio of lfHRV : hfHRV': 'lftohf',
             'Peak frequency of hfHRV': 'hf_peak',
             'Peak frequency of lfHRV': 'lf_peak'}


@Gooey(program_name='Physio pipeline',
       program_description='Physiological processing pipeline',
       default_size=(800, 1000))
def get_parser():
    """ Parser for GUI and command-line arguments """
    parser = GooeyParser()
    parser.add_argument('file_template', metavar='Filename template',
                        widget='FileChooser',
                        help='Select a representative file and replace '
                        'all subject-specific information with a "?" symbol. '
                        '\nE.g., subject_001_data.txt would become '
                        'subject_???_data.txt')

    inp_group = parser.add_argument_group('Inputs', 'Options to specify '
                                          'format of input files')
    inp_group.add_argument('--modality', metavar='Modality', default='ECG',
                           choices=['ECG', 'PPG', 'RESP'],
                           help='Modality of input data. Default: ECG')
    inp_group.add_argument('--fs', metavar='Sampling rate', default=1000,
                           type=float, help='Sampling rate of input data. '
                           'Default: 1000')
    inp_group.add_argument('--col', metavar='Column', default=0, type=int,
                           help='Which column of data to read from input '
                           'files. Default: 0')
    inp_group.add_argument('-d', '--header', metavar='Header',
                           action='store_true', help='Whether input files '
                           'have header (i.e., the first row of the file is a '
                           'description of the data)')

    out_group = parser.add_argument_group('Outputs', 'Options to specify '
                                          'format of output files')
    out_group.add_argument('-o', '--output', metavar='Filename',
                           default='peakdet.csv', help='Output filename. '
                           'Default: peakdet.csv')
    out_group.add_argument('-m', '--measurements', metavar='Measurements',
                           nargs='+', widget='Listbox',
                           choices=list(attr_conv.keys()),
                           help='Desired physiological measurements.\nChoose '
                           'multiple with ctrl+select')

    edit_group = parser.add_argument_group('Workflow argument (optional!)',
                                           'Options to specify modifications '
                                           'to workflow')
    edit_group.add_argument('-n', '--noedit', metavar='Editing',
                            action='store_true',
                            help='Turn off interactive editing.')
    edit_group.add_argument('-t', '--thresh', dest='thresh',
                            metavar='Threshold', default=None,
                            type=float, help='Threshold for peak '
                            'detection algorithm')

    return parser


def workflow(*, file_template, modality, fs, col, header, output, measurements,
             noedit, thresh):
    """
    Basic workflow for physiological data

    Parameters
    ----------
    file_template : str
        Template filename for data inputs
    modality : str
        One of [ECG, PPG, RESP]
    fs : float
        Sampling rate of input data
    col : int
        Column of input file where data is stored
    header : bool
        Whether input files have header
    output : str
        Path to output file
    measurements : list-of-str
        Desired output datapoints
    noedit : bool
        Whether to enable interactive editing
    thresh : float
        Threshold for peak detection
    """

    # output file
    print('OUTPUT FILE:\t\t{}\n'.format(output))
    # grab files from file template
    print('FILE TEMPLATE:\t{}\n'.format(file_template))
    files = glob.glob(file_template, recursive=True)

    # convert measurements to peakdet.HRV attribute friendly names
    print('REQUESTED MEASUREMENTS: {}\n'.format(', '.join(measurements)))
    measurements = [attr_conv[attr] for attr in measurements]

    # get appropriate modality
    peakfinder = modalities[modality]

    # check if output file exists -- if so, ensure headers will match
    head = 'filename,' + ','.join(measurements)
    if os.path.exists(output):
        with open(output, 'r') as src:
            eheader = src.readlines()[0]
        # if existing output file does not have same measurements are those
        # requested on command line, warn and use existing measurements so
        # as not to totally fork up existing file
        if eheader != head:
            warnings.warn('Desired output file exists and requested '
                          'measurements do not match with existing outputs '
                          'Using existing measurements, instead.')
            measurements = eheader.split(',')[1:]
        head = ''
    # if output file doesn't exist, nbd
    else:
        head += '\n'

    with open(output, 'a+') as dest:
        dest.write(head)
        # iterate through all files and do peak detection with manual editing
        for fname in files:
            print('Currently processing {}'.format(fname))
            # load data into class instance
            pf = peakfinder(fname, fs=fs, col=col, header=header)
            # perform peak detection
            if thresh is not None:
                pf.get_peaks(thresh=thresh)
            else:
                pf.get_peaks()
            # edit peaks, if desired (HIGHLY RECOMMENDED)
            if not noedit:
                pf.edit_peaks()
            # keep requested outputs
            hrv = peakdet.HRV(pf)
            outputs = ['{:.5f}'.format(getattr(hrv, attr, '')) for attr in
                       measurements]
            # save as we go so that interruptions don't screw everything up
            dest.write(','.join([fname] + outputs) + '\n')


def main():
    workflow(**vars(get_parser().parse_args()))


if __name__ == '__main__':
    main()
