# -*- coding: utf-8 -*-

import numpy as np
from scipy import signal
from scipy.interpolate import InterpolatedUnivariateSpline
from peakdet import physio
from peakdet.io import load


def check_physio(data, ensure_fs=True):
    """
    Checks that ``data`` is in correct format (i.e., ``peakdet.Physio``)

    Parameters
    ----------
    data : Physio_like
    ensure_fs : bool, optional
        Raise ValueError if ``data`` does not have a valid sampling rate
        attribute.

    Returns
    -------
    data : peakdet.Physio
        Loaded physio object

    Raises
    ------
    ValueError
        If `ensure_fs` is set and ``data`` doesn't have valid sampling rate
    """

    if not isinstance(data, physio.Physio):
        data = load(data)
    if ensure_fs and np.isnan(data.fs):
        raise ValueError('Provided data does not have valid sampling rate.')

    return data


def new_physio_like(ref_physio, data, fs=None, dtype=None):
    """
    Parameters
    ----------
    ref_physio : Physio_like
        Reference ``Physio`` object
    data : array_like
        Input physiological data
    fs : float, optional
        Sampling rate of ``data``. If not supplied, assumed to be the same as
        in ``ref_physio``
    dtype : data_type, optional
        Data type to convert ``data`` to, if conversion needed. Default: None

    Returns
    -------
    data : peakdet.Physio
        Loaded physio object with provided ``data``
    """

    if fs is None:
        fs = ref_physio.fs
    if dtype is None:
        dtype = ref_physio.data.dtype

    return ref_physio.__class__(np.asarray(data, dtype=dtype), fs=fs)


def filter_physio(data, cutoffs, method='bandpass'):
    """
    Performs frequency-based filtering on ``data``

    Parameters
    ----------
    data : Physio_like
        Input data to be filtered
    cutoffs : array_like
        Lower and/or upper bounds of filter (in Hz)
    method : str {'lowpass', 'highpass', 'bandpass', 'bandstop'}, optional
        Type of filter to use. Default: 'bandpass'

    Returns
    -------
    data : peakdet.Physio
        Filtered input data
    """

    _valid_methods = ['lowpass', 'highpass', 'bandpass', 'bandstop']

    data = check_physio(data)
    if method not in _valid_methods:
        raise ValueError('Provided method {} is not permitted; must be in {}.'
                         .format(method, _valid_methods))

    cutoffs = np.array(cutoffs)
    if method in ['lowpass', 'highpass'] and cutoffs.size != 1:
        raise ValueError('Cutoffs must be len 1 when using {} filter'
                         .format(method))
    elif method in ['bandpass', 'bandstop'] and cutoffs.size != 2:
        raise ValueError('Cutoffs must be len 2 when using {} filter'
                         .format(method))

    nyq_cutoff = cutoffs / (data.fs * 0.5)
    if np.any(nyq_cutoff > 1):
        raise ValueError('Provided cutoffs {} are outside of the Nyquist '
                         'frequency for input data with sampling rate {}.'
                         .format(cutoffs, data.fs))

    b, a = signal.butter(3, nyq_cutoff, btype=method)
    filtered = signal.filtfilt(b, a, data)

    return new_physio_like(data, filtered)


def interpolate_physio(data, fs):
    """
    Interpolates ``data`` to sampling rate ``fs``

    Parameters
    ----------
    data : Physio_like
        Input data to be interpolated
    fs : float
        Desired sampling rate to interpolate ``data``

    Returns
    -------
    data : peakdet.Physio
        Interpolated input data
    """

    data = check_physio(data)
    orig = np.arange(0, data.size / data.fs, 1 / data.fs)[:data.size]
    new = np.arange(0, orig[-1] + (1 / fs), 1 / fs)

    interpolated = InterpolatedUnivariateSpline(orig, data[:])(new)

    return new_physio_like(data, interpolated, fs=fs)
