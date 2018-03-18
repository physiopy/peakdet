# -*- coding: utf-8 -*-

import argparse
import os
import warnings
from gooey import Gooey, GooeyParser
import peakdet

modalities = dict(ECG=peakdet.ECG,
                  PPG=peakdet.PPG,
                  RESP=peakdet.RESP)


@Gooey
def get_parser():
    parser = GooeyParser(description='Physiological processing '
                                              'pipeline')
    parser.add_argument('files', nargs='+', help='Files to be processed',
                        widget='FileChooser')
    parser.add_argument('-o', '--output', metavar='file',
                        default='peakdet.csv', help='Output filename. '
                        'Default: peakdet.csv')
    parser.add_argument('--modality', default='ECG',
                        choices=['ECG', 'PPG', 'RESP'],
                        help='Modality of input data. Default: ECG')
    parser.add_argument('--fs', metavar='sampling rate', default=1000,
                        type=float, help='Sampling rate of input data. '
                        'Default: 1000')
    parser.add_argument('-m', '--measurements', nargs='+', widget='Listbox',
                        choices=['avgnn', 'rmssd', 'sdnn', 'hf', 'hf_log',
                                 'lf', 'lf_log'],
                        help='Desired physiological measurements')
    parser.add_argument('--col', metavar='column', default=0, type=int,
                        help='Which column of data to read from input files. '
                        'Default: 0')
    parser.add_argument('-d', '--header', dest='header', action='store_true',
                        help='Whether input files have header. Default: False')
    parser.add_argument('-n', '--noedit', action='store_true',
                        help='Turn off interactive editing.')
    parser.add_argument('-t', '--thresh', dest='thresh', default=None,
                        type=float, help=argparse.SUPPRESS)

    return parser


def main():
    options = get_parser().parse_args()
    peakfinder = modalities[options.modality]

    # check if output file exists -- if so, ensure headers will match
    header = 'filename,' + ','.join(options.measurements)
    if os.path.exists(options.output):
        with open(options.output, 'r') as src:
            eheader = src.readlines()[0]
        # if existing output file does not have same measurements are those
        # requested on command line, warn and use existing measurements so
        # as not to totally fork up existing file
        if eheader != header:
            warnings.warn('Desired output file exists and requested '
                          'measurements do not match with existing outputs '
                          'Using existing measurements, instead.')
            measurements = eheader.split(',')[1:]
        header = ''
    # if output file doesn't exist, nbd
    else:
        header += '\n'
        measurements = options.measurements[:]

    with open(options.output, 'a+') as dest:
        dest.write(header)
        # iterate through all files and do peak detection with manual editing
        for fname in options.files:
            # load data into class instance
            pf = peakfinder(fname, fs=options.fs,
                            col=options.col, header=options.header)

            # perform peak detection
            if options.thresh is not None:
                pf.get_peaks(thresh=options.thresh)
            else:
                pf.get_peaks()

            # edit peaks, if desired (HIGHLY RECOMMENDED)
            if not options.noedit:
                pf.edit_peaks()

            # keep requested outputs
            hrv = peakdet.HRV(pf)
            outputs = ['{:.5f}'.format(getattr(hrv, attr, None)) for attr in
                       measurements]

            # save as we go so that interruptions don't screw everything up
            dest.write(','.join([fname] + outputs) + '\n')


if __name__ == '__main__':
    main()
