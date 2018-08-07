# -*- coding: utf-8 -*-

import warnings
import numpy as np
from peakdet import io, utils


def load_rtpeaks(fname, channel, fs):
    """
    Loads data file as obtained from the `rtpeaks` Python module

    Data file `fname` should have a single, comma-delimited header of format:

        time,channelA,channelB,...,channelZ

    Raw data should be stored in columnar format, also comma-delimited, beneath
    this header. All data should be stored as integers. For more information,
    see the ``rtpeaks`` homepage: https://github.com/rmarkello/rtpeaks.

    Parameters
    ----------
    fname : str
        Path to data file to be loaded
    channel : int
        Integer corresponding to the channel number in `fname` from which data
        should be loaded
    fs : float
        Sampling rate at which `fname` was acquired

    Returns
    -------
    data : Physio_like
        Loaded physiological data
    """

    if fname.startswith('/'):
        warnings.warn('Provided file seems to be an absolute path. In order '
                      'to ensure full reproducibility it is recommended that '
                      'a relative path is provided.')

    with open(fname, 'r') as src:
        header = src.readline().strip().split(',')

    col = header.index('channel{}'.format(channel))
    data = np.loadtxt(fname, usecols=col, skiprows=1, delimiter=',')
    return io.load_physio(data, fs=fs, history=[utils._get_call()])
