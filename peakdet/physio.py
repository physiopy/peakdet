#!/usr/bin/env python

import os
import numpy as np
import scipy.signal
import scipy.spatial
from scipy.interpolate import InterpolatedUnivariateSpline
from sklearn.preprocessing import MinMaxScaler


class Physio(object):
    """Class to handle an instance of physiological data"""

    def __init__(self, file, fs):
        self.fname = file
        self.fs = float(fs)
        self.data = np.loadtxt(self.fname)


class ScaledPhysio(Physio):
    """Class that scales input data to [0.0, 1.0]"""

    def __init__(self, file, fs):
        super(ScaledPhysio,self).__init__(file,fs)

        scaler = MinMaxScaler(feature_range=(0,1))
        self.data = scaler.fit_transform(self.data.reshape(-1,1))


class FilteredPhysio(ScaledPhysio):
    """Class with bandpass filter method"""
    
    def __init__(self, file, fs):
        super(FilteredPhysio,self).__init__(file,fs)

        self.filtsig = self.data.copy()
        self.flims = gen_flims(self.data, self.fs)

    def reset(self):
        """Resets self.filtsig to original (scaled) data series"""
        self.filtsig = self.data.copy()

    def bandpass(self,flims=None):
        """Bandpass filters signal"""
        if not flims: flims = self.flims
        self.filtsig = bandpass_filt(self.filtsig, self.fs, flims)

    def lowpass(self, flims=None):
        """Lowpass filters signal"""
        if not flims: flims = self.flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[-1]
        self.filtsig = bandpass_filt(self.filtsig, self.fs, flims, btype='low')

    def highpass(self, flims=None):
        """Highpass filters signal"""
        if not flims: flims = self.flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[0]
        self.filtsig = bandpass_filt(self.filtsig, self.fs, flims, btype='high')


class InterpolatedPhysio(FilteredPhysio):
    """Class with data can be interpolation method"""

    def __init__(self, file, fs):
        super(InterpolatedPhysio,self).__init__(file,fs)

    def interpolate(self, order=2):
        """Interpolates data to `order` * `fs`"""
        self.rawdata, self.rawfs = self.data.copy(), self.fs

        t = np.arange(0, self.data.size/self.fs, 1./self.fs)
        tn = np.arange(0, t[-1], 1./(self.fs*order))
        i = InterpolatedUnivariateSpline(t,self.data)

        self.data, self.fs = i(tn), self.fs*order
        self.flims = gen_flims(self.data,self.fs)
        self.reset()

    def reset(self,hard=False):
        if hard:
            super(InterpolatedPhysio,self).__init__(self.fname,self.rawfs)
        else:
            super(InterpolatedPhysio,self).reset()

    def get_peaks(self, order=2):
        filt_inds = scipy.signal.argrelmax(self.filtsig,order=order)[0]
        raw_inds = scipy.signal.argrelmax(self.data,order=order)[0]

        peakinds = raw_inds[comp_peaks(filt_inds, raw_inds)]
        self.peakinds = peakinds[self.filtsig[peakinds] > self.filtsig.mean()]


def comp_peaks(p1,p2,k=2):
    """Compares lists of two indices to determine closest matches from `p1` in `p2`

    Parameters
    ----------
    p1, p2 : array-like, sorted
        Indices for comparing
    k : int
        How close indices should be in list

    Returns
    -------
    array : indices from `p2` that are closest to those in `p1`
    """

    kd = scipy.spatial.cKDTree(p2[:,None])
    on = kd.query(p1[:,None], k)[1]
    nn = np.ones((p1.shape[0],),dtype='int64') * -1
    used = set()

    for j, nj in enumerate(on):
        for k in nj:
            if k not in used:
                nn[j] = k
                used.add(k)
                break

    return nn


def flat_signal(signal):
    """Checks if >1D array can be flattened without data loss"""

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

    `flims` are the bounds of the filter. Utilizes butterworth filter
    from scipy.signal
    
    Parameters
    ----------
    signal : array-like
    fs : float
    flims : list-of-two
    btype : type of filter
    """
    
    signal = flat_signal(signal)
    if not flims: flims = [0,fs]

    nyq_freq = fs*0.5
    nyq_cutoff = np.array(flims)/nyq_freq
    b, a = scipy.signal.butter(3, nyq_cutoff, btype=btype)
    fsig = scipy.signal.filtfilt(b, a, signal)
    
    return fsig