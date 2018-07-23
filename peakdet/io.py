# -*- coding: utf-8 -*-

import warnings
import numpy as np
from peakdet import physio


def load(data, fs=None, dtype=None):
    """
    Returns ``Physio`` object with provided data

    Parameters
    ----------
    data : str or array_like or Physio_like
        Input physiological data. If array_like, should be one-dimensional
    fs : float, optional
        Sampling rate of ``data``. Default: None
    dtype : data_type, optional
        Data type to convert ``data`` to, if conversion needed. Default: None

    Returns
    -------
    data: peakdet.Physio
        Loaded physio object

    Raises
    ------
    TypeError
        If provided ``data`` is unable to be loaded
    """

    if isinstance(data, str):
        try:
            data = np.load(data)
            phys = physio.Physio(**data)
        except IOError:
            data = np.loadtxt(data)
            phys = physio.Physio(data)
    elif isinstance(data, np.ndarray):
        return physio.Physio(np.asarray(data, dtype=dtype), fs=fs)
    elif not isinstance(data, physio.Physio):
        raise TypeError('Cannot load data of type {}'.format(type(data)))

    if fs is not None and fs != phys.fs:
        if not np.isnan(phys.fs):
            warnings.warn('Provided sampling rate does not match loaded rate. '
                          'Resetting loaded sampling rate {} to provided {}'
                          .format(phys.fs, fs))
        phys._fs = fs
    if dtype is not None:
        phys._data = np.asarray(phys[:], dtype=dtype)

    return phys


def save(file, data):
    """
    Saves ``data`` to ``fname`

    Parameters
    ----------
    fname : str
        Path to output file; .phys will be appended if necessary
    data : Physio_like
        Data to be saved to file
    """

    from peakdet.utils import check_physio

    data = check_physio(data)
    file += '.phys' if not file.endswith('.phys') else ''
    with open(file, 'wb') as dest:
        np.savez_compressed(dest, data=data.data, fs=data.fs)


def load_rtpeaks(fname, channel, fs):
    """
    Loads data file as obtained from the `rtpeaks` Python module

    Data file `fname` should have a single, comma-delimited header row:

        time,channelA,channelB,...,channelZ

    Raw data should be stored in columnar format, also comma-delimited, beneath
    this header, and should be integer-based. For more information, see the
    rtpeaks homepage at https://github.com/rmarkello/rtpeaks.

    Parameters
    ----------
    fname : str
        Path to data file
    channel : int
        This corresponds to the channel number for which data should be loaded
    fs : float
        Sampling rate at which data was acquired

    Returns
    -------
    data : Physio_like
        Loaded data
    """

    with open(fname, 'r') as src:
        header = src.readline().strip().split(',')

    col = header.index('channel{}'.format(channel))
    data = np.loadtxt(fname, usecols=col, skiprows=1, delimiter=',')

    return load(data, fs=fs)
