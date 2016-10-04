#!/usr/bin/env python

import numpy as np
import scipy.signal
from scipy.spatial import cKDTree

def comp_peaks(raw_data, filtered_data, order=2, comparator=scipy.signal.argrelmax):
    """Finds peaks/troughs in raw/filtered data; returns peaks in raw data closest to those in filtered

    Parameters
    ----------
    raw_data : array-like
    filtered_data : array-like
    order : int
    comparator : function
        Choose from scipy.signal.argrelmax, scipy.signal.argrelmin
    """
    if comparator != scipy.signal.argrelmax and comparator != scipy.signal.argrelmin:
        raise TypeError("Comparator is not a valid selection")

    filtered_inds = comparator(filtered_data,order=order)[0]
    raw_inds = comparator(raw_data, order=order)[0]

    inds = raw_inds[comp_lists(filtered_inds, raw_inds)]

    return inds


def comp_lists(l1,l2,k=2):
    """Compares lists of two indices to determine closest matches from `l1` in `l2`

    Parameters
    ----------
    l1, l2 : array-like, sorted
        Indices to compare
    k : int
        How close indices should be in lists

    Returns
    -------
    array : indices from `l2` that are closest to those in `l1`
    """

    kd = cKDTree(l2[:,None])
    on = kd.query(l1[:,None], k)[1]
    nn = np.ones((l1.shape[0],),dtype='int64') * -1
    used = set()

    for j, nj in enumerate(on):
        for k in nj:
            if k not in used:
                nn[j] = k
                used.add(k)
                break

    return nn


def flat_signal(signal):
    """Checks if >1D array can be flattened without data loss; flattens

    Parameters
    ----------
    signal : array-like

    Returns
    -------
    array-like : potentially flattened
    """

    if signal.ndim > 1:
        if signal.shape[-1] == 1:
            signal = signal.flatten()

    return signal
    

def gen_flims(signal,fs):
    """Generates a 'best guess' of ideal frequency cutoffs for a bp filter

    Parameters
    ----------
    signal : array-like
    fs : float

    Returns
    -------
    list-of-two : optimal frequency cutoffs
    """

    signal = flat_signal(signal)

    m, s = signal.mean(), signal.std()
    inds = scipy.signal.argrelmax(signal, order=2)[0]
    hinds = inds[signal[inds] > m+s]
    mfreq = np.mean(hinds[1:] - hinds[:-1])/fs

    return [mfreq/2, mfreq*2]


def bandpass_filt(signal,fs,flims=None,btype='bandpass'):
    """Runs `btype` filter on `signal` of sampling rate `fs`
    
    Parameters
    ----------
    signal : array-like
    fs : float
    flims : array-like
        Bounds of filter
    btype : str
        Type of filter; from ['band','low','high']
    """
    
    signal = flat_signal(signal)
    if not flims: flims = [0,fs]

    nyq_freq = fs*0.5
    nyq_cutoff = np.asarray(flims)/nyq_freq
    b, a = scipy.signal.butter(3, nyq_cutoff, btype=btype)
    fsig = scipy.signal.filtfilt(b, a, signal)
    
    return fsig