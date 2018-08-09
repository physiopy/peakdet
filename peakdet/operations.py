# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.interpolate import InterpolatedUnivariateSpline
from peakdet import editor, utils


def filter_physio(data, cutoffs, method):
    """
    Applies a 3rd-order digital Butterworth filter of type `method` to `data`

    Parameters
    ----------
    data : Physio_like
        Input data to be filtered
    cutoffs : int or list
        If `method` is 'lowpass' or 'highpass', an integer specifying the lower
        or upper bound of the filter (in Hz). If method is 'bandpass' or
        'bandstop', a list specifying the lower _and_ upper bound of the filter
        (in Hz).
    method : {'lowpass', 'highpass', 'bandpass', 'bandstop'}
        The type of filter to apply to `data`.

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
        raise ValueError('Cutoffs must be length 1 when using {} filter'
                         .format(method))
    elif method in ['bandpass', 'bandstop'] and cutoffs.size != 2:
        raise ValueError('Cutoffs must be length 2 when using {} filter'
                         .format(method))

    nyq_cutoff = cutoffs / (data.fs * 0.5)
    if np.any(nyq_cutoff > 1):
        raise ValueError('Provided cutoffs {} are outside of the Nyquist '
                         'frequency for input data with sampling rate {}.'
                         .format(cutoffs, data.fs))

    b, a = signal.butter(3, nyq_cutoff, btype=method)
    filtered = utils.new_physio_like(data, signal.filtfilt(b, a, data))

    # log filter in history
    filtered._history += [utils._get_call()]

    return filtered


def interpolate_physio(data, target_fs):
    """
    Interpolates `data` to desired sampling rate `target_fs`

    Parameters
    ----------
    data : Physio_like
        Input data to be interpolated
    target_fs : float
        Desired sampling rate for `data`

    Returns
    -------
    interp : peakdet.Physio
        Interpolated input data
    """

    data = utils.check_physio(data, ensure_fs=True)

    # generate original and target "time" series
    orig = np.arange(0, len(data.data) / data.fs, 1 / data.fs)[:len(data.data)]
    new = np.arange(0, orig[-1] + (1 / target_fs), 1 / target_fs)

    interp = InterpolatedUnivariateSpline(orig, data[:])(new)
    interp = utils.new_physio_like(data, interp, fs=target_fs)
    interp._history += [utils._get_call()]

    return interp


def peakfind_physio(data, *, thresh=0.2, dist=None):
    """
    Finds peaks in `data`

    Parameters
    ----------
    data : Physio_like
        Input data in which to find peaks
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
    # second, more thorough peak detection
    data._metadata.peaks = utils.find_peaks(data, dist=cdist, thresh=thresh)
    # perform trough detection based on detected peaks
    data._metadata.troughs = utils.check_troughs(data, data.peaks, [])

    data._history += [utils._get_call()]
    return data


def edit_physio(data, *, delete=None, reject=None):
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
    # replay editing
    else:
        if reject is not None:
            data = editor.reject_peaks(data, remove=reject)[0]
        if delete is not None:
            data = editor.delete_peaks(data, remove=delete)[0]

    data._history += [utils._get_call()]

    return data


def plot_physio(data, *, ax=None):
    """
    Small utility for plotting `data` with any detected peaks / troughs

    Parameters
    ----------
    data : Physio_like
        Physiological data to plot
    ax : matplotlib.axes.Axis, optional
        Axis to plot `data` on. Default: None
    """

    fs = 1 if data.fs is None else data.fs
    time = np.arange(0, len(data.data) / fs, 1 / fs)
    if ax is None:
        fig, ax = plt.subplots(1, 1)
    ax.plot(time, data, 'b',
            time[data.peaks], data[data.peaks], '.r',
            time[data.troughs], data[data.troughs], '.g')

    return ax