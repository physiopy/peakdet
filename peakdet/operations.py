# -*- coding: utf-8 -*-
"""
Functions for processing and interpreting physiological data
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate, signal
from peakdet import editor, utils

@utils.make_operation()
def filter_physio(data, cutoffs, method, *, order=3):
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

    return filtered


@utils.make_operation()
def interpolate_physio(data, target_fs, *, kind='cubic'):
    """
    Interpolates `data` to desired sampling rate `target_fs`

    Parameters
    ----------
    data : Physio_like
        Input physiological data to be interpolated
    target_fs : float
        Desired sampling rate for `data`
    kind : str or int, optional
        Type of interpolation to perform. Must be one of available kinds in
        :func:`scipy.interpolate.interp1d`. Default: 'cubic'

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
    interp = interpolate.interp1d(t_orig, data, kind=kind)(t_new)
    if data.suppdata is None:
        suppinterp = None
    else:
        suppinterp = interpolate.interp1d(t_orig, data.suppdata, kind=kind)(t_new)
    interp = utils.new_physio_like(data, interp, fs=target_fs, suppdata=suppinterp)

    return interp


@utils.make_operation()
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
    thresh = np.squeeze(np.diff(np.percentile(data, [5, 95]))) * thresh
    locs, heights = signal.find_peaks(data[:], distance=cdist, height=thresh)

    # second, more thorough peak detection
    cdist = np.diff(locs).mean() // 2
    heights = np.percentile(heights['peak_heights'], 1)
    locs, heights = signal.find_peaks(data[:], distance=cdist, height=heights)
    data._metadata['peaks'] = locs
    # perform trough detection based on detected peaks
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks)

    return data


@utils.make_operation()
def delete_peaks(data, remove):
    """
    Deletes peaks in `remove` from peaks stored in `data`

    Parameters
    ----------
    data : Physio_like
    remove : array_like

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=True)
    data._metadata['peaks'] = np.setdiff1d(data._metadata['peaks'], remove)
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks, data.troughs)

    return data


@utils.make_operation()
def reject_peaks(data, remove):
    """
    Marks peaks in `remove` as rejected artifacts in `data`

    Parameters
    ----------
    data : Physio_like
    remove : array_like

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=True)
    data._metadata['reject'] = np.append(data._metadata['reject'], remove)
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks, data.troughs)

    return data


@utils.make_operation()
def add_peaks(data, add):
    """
    Add `newpeak` to add them in `data`

    Parameters
    ----------
    data : Physio_like
    add : int

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=True)
    idx = np.searchsorted(data._metadata['peaks'], add)
    data._metadata['peaks'] = np.insert(data._metadata['peaks'], idx, add)
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks)

    return data


@utils.make_operation()
def add_peaks(data, add):
    """
    Add `newpeak` to add them in `data`

    Parameters
    ----------
    data : Physio_like
    add : int

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=True)
    idx = np.searchsorted(data._metadata['peaks'], add)
    data._metadata['peaks'] = np.insert(data._metadata['peaks'], idx, add)
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks)

    return data


def edit_physio(data):
    """
    Opens interactive plot with `data` to permit manual editing of time series

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited

    Returns
    -------
    edited : :class:`peakdet.Physio`
        Input `data` with manual edits
    """

    data = utils.check_physio(data, ensure_fs=True)

    # no point in manual edits if peaks/troughs aren't defined
    if not (len(data.peaks) and len(data.troughs)):
        return

    # perform manual editing
    edits = editor._PhysioEditor(data)
    plt.show(block=True)

    # replay editing on original provided data object
    if len(edits.rejected) > 0:
        data = reject_peaks(data, remove=sorted(edits.rejected))
    if len(edits.deleted) > 0:
        data = delete_peaks(data, remove=sorted(edits.deleted))
    if len(edits.included) > 0:
        data = add_peaks(data, add=sorted(edits.included))

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
