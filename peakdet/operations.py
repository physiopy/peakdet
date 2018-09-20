# -*- coding: utf-8 -*-
"""
Functions for processing and interpreting physiological data
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.interpolate import InterpolatedUnivariateSpline
from peakdet import editor, utils


def filter_physio(data, cutoffs, method, order=3):
    """
    Applies an `order`-order digital `method` Butterworth filter to `data`

    Parameters
    ----------
    data : Physio_like
        Input physiological data to be filtered
    cutoffs : int or list
        If `method` is 'lowpass' or 'highpass', an integer specifying the lower
        or upper bound of the filter (in Hz). If method is 'bandpass' or
        'bandstop', a list specifying the lower and upper bound of the filter
        (in Hz).
    method : {'lowpass', 'highpass', 'bandpass', 'bandstop'}
        The type of filter to apply to `data`
    order : int, optional
        Order of filter to be applied. Default: 3

    Returns
    -------
    filtered : :class:`peakdet.Physio`
        Filtered input `data`
    """

    _valid_methods = ['lowpass', 'highpass', 'bandpass', 'bandstop']

    data = utils.check_physio(data, ensure_fs=True)
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

    b, a = signal.butter(int(order), nyq_cutoff, btype=method)
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
        Input physiological data to be interpolated
    target_fs : float
        Desired sampling rate for `data`

    Returns
    -------
    interp : :class:`peakdet.Physio`
        Interpolated input `data`
    """

    data = utils.check_physio(data, ensure_fs=True)

    factor = target_fs / data.fs

    # generate original and target "time" series
    t_orig = np.linspace(0, len(data) / data.fs, len(data))
    t_new = np.linspace(0, len(data) / data.fs, int(len(data) * factor))

    # interpolate data and generate new Physio object
    interp = InterpolatedUnivariateSpline(t_orig, data[:])(t_new)
    interp = utils.new_physio_like(data, interp, fs=target_fs)
    # add call to history
    interp._history += [utils._get_call()]

    return interp


def peakfind_physio(data, *, thresh=0.2, dist=None):
    """
    Performs peak and trough detection on `data`

    Parameters
    ----------
    data : Physio_like
        Input data in which to find peaks
    thresh : float [0,1], optional
        Relative height threshold a data point must surpass to be classified as
        a peak. Default: 0.2
    dist : int, optional
        Distance in indices that peaks must be separated by in `data`. If None,
        this is estimated. Default: None

    Returns
    -------
    peaks : :class:`peakdet.Physio`
        Input `data` with detected peaks and troughs
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
    # add call to history
    data._history += [utils._get_call()]

    return data


def edit_physio(data, *, delete=None, reject=None):
    """
    Opens interactive plot with `data` to permit manual editing of time series

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    delete : array_like, optional
        List or array of indices to delete from peaks associated with `data`.
        Default: None
    reject : array_like, optional
        List or array of indices to reject from peaks associated with `data`.
        Default: None

    Returns
    -------
    edited : :class:`peakdet.Physio`
        Input `data` with manual (or specified) edits
    """

    # check if we need fs info
    if delete is None and reject is None:
        ensure_fs = True
    else:
        ensure_fs = False
    data = utils.check_physio(data, ensure_fs=ensure_fs, copy=True)

    # no point in manual edits if peaks/troughs aren't defined
    if not (len(data.peaks) and len(data.troughs)):
        return
    # perform manual editing
    if delete is None and reject is None:
        edits = editor._PhysioEditor(data)
        plt.show(block=True)
        delete, reject = edits.deleted, edits.rejected
    # replay editing (or accept a priori edits)
    else:
        if reject is not None:
            data = editor.reject_peaks(data, remove=reject)[0]
        if delete is not None:
            data = editor.delete_peaks(data, remove=delete)[0]
    # add call to history
    data._history += [utils._get_call()]

    return data


def plot_physio(data, *, ax=None):
    """
    Plots `data` and associated peaks / troughs

    Parameters
    ----------
    data : Physio_like
        Physiological data to plot
    ax : :class:`matplotlib.axes.Axes`, optional
        Axis on which to plot `data`. If None, a new axis is created. Default:
        None

    Returns
    -------
    ax : :class:`matplotlib.axes.Axes`
        Axis with plotted `data`
    """

    # generate x-axis time series
    fs = 1 if np.isnan(data.fs) else data.fs
    time = np.arange(0, len(data) / fs, 1 / fs)
    if ax is None:
        fig, ax = plt.subplots(1, 1)
    # plot data with peaks + troughs, as appropriate
    ax.plot(time, data, 'b',
            time[data.peaks], data[data.peaks], '.r',
            time[data.troughs], data[data.troughs], '.g')

    return ax
