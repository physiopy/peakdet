# -*- coding: utf-8 -*-

import inspect
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.interpolate import InterpolatedUnivariateSpline
from peakdet import editor, utils


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
    filtered : peakdet.Physio
        Filtered input data
    """

    _valid_methods = ['lowpass', 'highpass', 'bandpass', 'bandstop']

    data = utils.check_physio(data)
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
    filtered = utils.new_physio_like(data, signal.filtfilt(b, a, data))

    # log filter in history
    filtered.history.append((inspect.stack(0)[0].function,
                             dict(cutoffs=cutoffs.tolist(), method=method)))

    return filtered


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
    interp : peakdet.Physio
        Interpolated input data
    """

    data = utils.check_physio(data)
    orig = np.arange(0, data.size / data.fs, 1 / data.fs)[:data.size]
    new = np.arange(0, orig[-1] + (1 / fs), 1 / fs)

    interp = InterpolatedUnivariateSpline(orig, data[:])(new)
    interp = utils.new_physio_like(data, interp, fs=fs)
    interp.append((inspect.stack(0)[0].function, dict(fs=fs)))

    return interp


def peakfind_physio(data, thresh=0.2, dist=None):
    """
    Finds peaks in `data`

    Parameters
    ----------
    data : Physio_like
    thresh : float [0,1], optional
        Relative height threshold data must surpass to be classified as a
        peak. Default: 0.2
    dist : int, optional
        Distance (in indices) that peaks must be separated by. If not
        specified, this is estimated from data.
    """

    # let's not alter things in-place
    data = utils.new_physio_like(data, data.data)

    if dist is None:
        dist = data.fs // 4

    locs = utils.find_peaks(data, dist=dist, thresh=thresh)
    dist = np.diff(locs).mean() // 2
    data._metadata.peaks = utils.find_peaks(data, dist=dist, thresh=thresh)
    troughs = _find_troughs(data, thresh=thresh, dist=dist)
    data._metadata.troughs = utils.check_troughs(data, data.peaks, troughs)

    data.history.append((inspect.stack(0)[0].function,
                         dict(thresh=thresh, dist=dist)))
    return data


def _find_troughs(data, thresh=0.4, dist=None):
    """
    Detects troughs in data

    Parameters
    ----------
    data : Physio_like
    thresh : float [0,1], optional
        Relative height threshold data must surpass to be classified as a
        trough. Default: 0.2
    dist : int, optional
        Distance (in indices) that troughs must be separated by. If not
        specified, this is estimated from data.
    """

    if dist is None:
        dist = data.fs // 4

    locs = utils.find_troughs(data, dist=dist, thresh=thresh)
    dist = np.diff(locs).mean() // 2
    troughs = utils.find_troughs(data, dist=dist, thresh=thresh)

    return troughs


def edit_physio(data, delete=None, reject=None):
    """
    Returns interactive physio editor for `data`

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    """

    if not (len(data.peaks) and len(data.troughs)):
        return
    if delete is None and reject is None:
        int = plt.rcParams['interactive']
        if int:
            plt.ioff()
        e = editor._PhysioEditor(data)
        plt.show()
        if int:
            plt.ion()
