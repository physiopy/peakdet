#!/usr/bin/env python

import os
import numpy as np
import scipy.signal
from scipy.interpolate import InterpolatedUnivariateSpline
from sklearn.preprocessing import MinMaxScaler


class Physio(object):
    """Class to handle an instance of physiological data"""

    def __init__(self, file, fs):
        self.fname = file
        self.fs = fs
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
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[0]
        self.filtsig = bandpass_filt(self.filtsig, self.fs, flims, btype='lowpass')


class InterpolatedPhysio(FilteredPhysio):
    """Class where input data is auto-interpolated to fs*2"""

    def __init__(self, file, fs):
        super(InterpolatedPhysio,self).__init__(file,fs)

        t = np.arange(0, self.data.size/self.fs, 1./self.fs)
        tn = np.arange(0, t[-1], 1./(self.fs*2))
        i = InterpolatedUnivariateSpline(t,self.data)

        self.data = i(tn)
        self.fs = self.fs*2
        self.reset()
        self.flims = gen_flims(self.data,self.fs)


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