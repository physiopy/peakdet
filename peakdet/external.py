# -*- coding: utf-8 -*-
"""
Functions for interacting with physiological data acquired by external packages
"""

import warnings

import numpy as np

from peakdet import physio, utils


@utils.make_operation(exclude=[])
def load_rtpeaks(fname, channel, fs):
    """
    Loads data file as obtained from the ``rtpeaks`` Python module

    Data file `fname` should have a single, comma-delimited header of format:

        time,channel#,channel#,...,channel#

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
    data : :class:`peakdet.Physio`
        Loaded physiological data
    """

    if fname.startswith("/"):
        warnings.warn(
            "Provided file seems to be an absolute path. In order "
            "to ensure full reproducibility it is recommended that "
            "a relative path is provided."
        )

    with open(fname, "r") as src:
        header = src.readline().strip().split(",")

    col = header.index("channel{}".format(channel))
    data = np.loadtxt(fname, usecols=col, skiprows=1, delimiter=",")
    phys = physio.Physio(data, fs=fs)

    return phys
