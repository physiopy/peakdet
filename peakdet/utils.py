# -*- coding: utf-8 -*-
"""
Various utilities for processing physiological data. These should not be called
directly but should support wrapper functions stored in `peakdet.operations`.
"""

import inspect
import numpy as np
from scipy.stats import zscore
from sklearn.utils import Bunch
from peakdet import physio
from peakdet.io import load_physio


def _get_call(*, exclude=['data'], serializable=True):
    """
    Returns calling function name and dict of provided arguments (name : value)

    Parameters
    ----------
    exclude : list, optional
        What arguments to exclude from provided argument : value dictionary.
        Default: ['data']
    serializable : bool, optional
        Whether to coerce argument values to JSON serializable form. Default:
        True

    Returns
    -------
    function: str
        Name of calling function
    provided : dict
        Dictionary of function arguments and provided values
    """

    if not isinstance(exclude, list):
        exclude = [exclude]

    # get one function call up the stack (the bottom is _this_ function)
    calling = inspect.stack(0)[1]
    frame, function = calling.frame, calling.function

    # get all the args / kwargs from the calling function
    argspec = inspect.getfullargspec(frame.f_globals[function])
    args = argspec.args + argspec.kwonlyargs

    # save arguments + argument values for everything not in `exclude`
    provided = {k: frame.f_locals[k] for k in args if k not in exclude}

    # if we want `provided` to be serializable, we can do a little cleaning up
    # this is NOT foolproof, but will coerce numpy arrays to lists which tends
    # to be the main issue with these sorts of things
    if serializable:
        for k, v in provided.items():
            if hasattr(v, 'tolist'):
                provided[k] = v.tolist()

    return function, provided


def check_physio(data, ensure_fs=True, copy=False):
    """
    Checks that `data` is in correct format (i.e., `peakdet.Physio`)

    Parameters
    ----------
    data : Physio_like
    ensure_fs : bool, optional
        Raise ValueError if `data` does not have a valid sampling rate
        attribute.
    copy: bool, optional
        Whether to return a copy of the provided data. Default: False

    Returns
    -------
    data : peakdet.Physio
        Loaded physio object

    Raises
    ------
    ValueError
        If `ensure_fs` is set and `data` doesn't have valid sampling rate
    """

    if not isinstance(data, physio.Physio):
        data = load_physio(data)
    if ensure_fs and np.isnan(data.fs):
        raise ValueError('Provided data does not have valid sampling rate.')
    if copy is True:
        return new_physio_like(data, data.data,
                               copy_history=True,
                               copy_metadata=True)
    return data


def new_physio_like(ref_physio, data, *, fs=None, dtype=None,
                    copy_history=True, copy_metadata=True):
    """
    Makes `data` into physio object like `ref_data`

    Parameters
    ----------
    ref_physio : Physio_like
        Reference `Physio` object
    data : array_like
        Input physiological data
    fs : float, optional
        Sampling rate of `data`. If not supplied, assumed to be the same as
        in `ref_physio`
    dtype : data_type, optional
        Data type to convert `data` to, if conversion needed. Default: None
    copy_history : bool, optional
        Copy history from `ref_physio` to new physio object. Default: True

    Returns
    -------
    data : peakdet.Physio
        Loaded physio object with provided `data`
    """

    if fs is None:
        fs = ref_physio.fs
    if dtype is None:
        dtype = ref_physio.data.dtype
    history = ref_physio.history.copy() if copy_history else []
    metadata = Bunch(**ref_physio._metadata) if copy_metadata else None

    # make new class
    out = ref_physio.__class__(np.asarray(data, dtype=dtype),
                               fs=fs, history=history, metadata=metadata)
    return out


def get_extrema(data, peaks=True, thresh=0.4):
    """
    Find extrema in `data` by changes in sign of first derivative

    Parameters
    ----------
    data : array_like or Physio_like
        Input data on which to perform extrema detection
    peaks : bool, optional
        Whether to look for peaks instead of troughs. Default: True
    thresh : float (0, 1), optional
        Amplitude based threshold

    Returns
    -------
    locs : np.ndarray
        Indices of extrema from `data`
    """

    if thresh < 0 or thresh > 1:
        raise ValueError('Provided threshold {} is not in range [0, 1]. '
                         'Please provide a valid threshold.'
                         .format(thresh))

    if peaks:
        uthresh = (thresh * np.diff(np.percentile(data, [5, 95])))
        Indx = np.argwhere(data > uthresh).squeeze()
    else:
        uthresh = (thresh * np.diff(np.percentile(data, [95, 5])))
        Indx = np.argwhere(data < uthresh).squeeze()

    trend = np.sign(np.diff(data))
    idx = np.argwhere(trend == 0).squeeze()

    for i in range(idx.size - 1, -1, -1):
        gtz = trend[min(idx[i] + 1, trend.size - 1)] >= 0
        trend[idx[i]] = 1 if gtz else -1

    idx = np.argwhere(np.diff(trend) == (-2 if peaks else 2)).squeeze() + 1

    return np.intersect1d(Indx, idx)


def min_peak_dist(data, locs, peaks=True, dist=250):
    """
    Ensures `locs` in `data` are separated by at least `dist`

    Parameters
    ----------
    data : array_like or Physio_like
        Input data for which `locs` were detected
    locs : array_like
        Extrema in `data`, typically from `get_extrema()`
    peaks : bool, optional
        Whether to look for peaks instead of troughs. Default: True
    dist : int, optional
        Minimum required distance (in datapoints) b/w `locs`. Default: 250

    Returns
    -------
    locs : np.ndarray
        Extrema separated by at least `dist`
    """

    if not any(np.diff(sorted(locs)) <= dist):
        return locs

    idx = data[locs].argsort()
    if peaks:
        idx = idx[::-1]
    locs = locs[idx]
    idelete = np.zeros_like(locs, dtype=bool)

    for i in range(locs.size):
        if not idelete[i]:
            dist_diff = np.logical_and(locs >= locs[i] - dist,
                                       locs <= locs[i] + dist)
            idelete = np.logical_or(idelete, dist_diff)
            idelete[i] = 0

    return np.sort(locs[~idelete])


def find_peaks(data, thresh=0.4, dist=250):
    """
    Finds peaks in `data`

    Parameters
    ----------
    data : array_like or Physio_like
        Input data on which to perform peak detection
    thresh : float (0, 1), optional
        Amplitude based threshold
    dist : int
        Minimum required distance (in datapoints) b/w peaks in `data`

    Returns
    -------
    peaks : np.ndarray
        Indices of peak locations in `data`
    """

    extrema = get_extrema(data, thresh=thresh)
    peaks = min_peak_dist(data, extrema, dist=dist)

    return peaks.astype(int)


def find_troughs(data, thresh=0.4, dist=250):
    """
    Finds troughs in `data`

    Parameters
    ----------
    data : array_like or Physio_like
        Input data on which to perform trough detection
    thresh : float (0, 1), optional
        Amplitude based threshold
    dist : int
        Minimum required distance (in datapoints) b/w troughs in `data`

    Returns
    -------
    troughs : np.ndarray
        Indices of trough locations in `data`
    """

    extrema = get_extrema(data, peaks=False, thresh=thresh)
    troughs = min_peak_dist(data, extrema, peaks=False, dist=dist)

    return troughs.astype(int)


def check_troughs(data, peaks, troughs):
    """
    Confirms that `troughs` exists between every set of `peaks` in `data`

    Parameters
    ----------
    data : array-like
        Input data for which `troughs` and `peaks` were detected
    peaks : array-like
        Indices of suspected peak locations in `data`
    troughs : array-like
        Indices of suspected trough locations in `data`

    Returns
    -------
    troughs : np.ndarray
        Indices of trough locations in `data`, dependent on `peaks`
    """

    all_troughs = np.zeros(peaks.size - 1, dtype=int)

    for f in range(peaks.size - 1):
        curr = np.logical_and(troughs > peaks[f],
                              troughs < peaks[f + 1])
        if not np.any(curr):
            dp = data[peaks[f]:peaks[f + 1]]
            idx = peaks[f] + np.argwhere(dp == dp.min())[0]
        else:
            idx = troughs[curr]
            if idx.size > 1:
                idx = idx[0]
        all_troughs[f] = idx

    return all_troughs


def gen_temp(data, locs, factor=0.5):
    """
    Generate waveform template array from `data`

    Waveforms are taken from around peak locations in `locs`

    Parameters
    ----------
    data : array_like
    locs : arrray_like
        Indices of suspected peak locations
    factor: float (0, 1), optional

    Returns
    -------
    array : peak waveforms
    """

    avgrate = round(np.diff(locs).mean())
    THW = int(np.ceil(factor * (avgrate / 2)))
    nsamptemp = (THW * 2) + 1
    npulse = locs.size
    template = np.zeros([npulse - 2, nsamptemp])

    for n in range(1, npulse - 1):
        template[n - 1] = data[locs[n] - THW:locs[n] + THW + 1]
        template[n - 1] = template[n - 1] - template[n - 1].mean()
        template[n - 1] = template[n - 1] / max(abs(template[n - 1]))

    return template


def corr(x, y, zscored=[False, False]):
    """
    Potentially faster correlation of `x` and `y`

    Will z-transform data before correlation.

    Parameters
    ----------
    x : array, n x 1
    y : array, n x 1
    zscored : [bool, bool]
        Whether x and y, respectively, have been z-transformed

    Returns
    -------
    float : [0,1] correlation between `x` and `y`
    """

    x, y = np.asarray(x).squeeze(), np.asarray(y).squeeze()

    if x.ndim > 1 or y.ndim > 1:
        raise ValueError('Input arrays must have only one dimension.')
    if x.size != y.size:
        raise ValueError('Input array dimensions must be same size.')

    # numpy corrcoef is faster if both variables need to be z-scored
    if not np.any(zscored):
        return np.corrcoef(x, y)[0, 1]

    if not zscored[0]:
        x = zscore(x, ddof=1)
    if not zscored[1]:
        y = zscore(y, ddof=1)

    return np.dot(x.T, y) * (1. / (x.size - 1))


def corr_template(temp, sim=0.95):
    """
    Generates single waveform template from output of `gen_temp`.

    Correlates each row of `temp` to averaged template and selects rows with
    correlation >=`sim` for use in final, averaged template.

    Parameters
    ----------
    temp : array of waveforms
    sim : float (0,1)
        Cutoff for correlation of waveforms to average template

    Returns
    -------
    array : template waveform
    """

    npulse = temp.shape[0]

    mean_temp = zscore(temp.mean(axis=0), ddof=1)
    sim_to_temp = np.zeros((temp.shape[0], 1))

    for n in range(temp.shape[0]):
        sim_to_temp[n] = corr(temp[n], mean_temp, [False, True])

    good_temp_ind = np.where(sim_to_temp > sim)[0]
    if good_temp_ind.shape[0] >= np.ceil(npulse * 0.1):
        clean_temp = temp[good_temp_ind]
    else:
        new_temp_ind = np.where(sim_to_temp >
                                (1 - np.ceil(npulse * 0.1) / npulse))[0]
        clean_temp = np.atleast_2d(temp[new_temp_ind]).T

    return clean_temp.mean(axis=0)
