# -*- coding: utf-8 -*-

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
    filtered.history += [utils._get_call()]

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

    data = utils.check_physio(data, copy=True)
    orig = np.arange(0, data.size / data.fs, 1 / data.fs)[:data.size]
    new = np.arange(0, orig[-1] + (1 / fs), 1 / fs)

    interp = InterpolatedUnivariateSpline(orig, data[:])(new)
    interp = utils.new_physio_like(data, interp, fs=fs)
    interp.history += [utils._get_call()]

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

    ensure_fs = True if dist is None else False
    data = utils.check_physio(data, ensure_fs=ensure_fs, copy=True)

    # first pass peak detection to get approximate distance between peaks
    cdist = data.fs // 4 if dist is None else dist
    locs = utils.find_peaks(data, dist=cdist, thresh=thresh)
    cdist = np.diff(locs).mean() // 2
    # second more thorough peak detection
    data._metadata.peaks = utils.find_peaks(data, dist=cdist, thresh=thresh)
    # perform trough detection based on detected peaks
    data._metadata.troughs = utils.check_troughs(data, data.peaks, [])

    data.history += [utils._get_call()]
    return data


def edit_physio(data, delete=None, reject=None):
    """
    Returns interactive physio editor for `data`

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    """

    # let's not alter things in-place
    data = utils.check_physio(data, copy=True)
    # no point in manual edits if peaks/troughs aren't defined
    if not (len(data.peaks) and len(data.troughs)):
        return
    # perform manual editing
    if delete is None and reject is None:
        edits = editor._PhysioEditor(data)
        plt.show(block=True)
        delete, reject = edits.deleted, edits.rejected

    data.history += [utils._get_call()]
    return data
