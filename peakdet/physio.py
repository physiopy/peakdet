#!/usr/bin/env python

import os
import numpy as np
import scipy.signal
from sklearn.preprocessing import MinMaxScaler

class Physio(object):
    """Class to handle an instance of physiological data"""

    def __init__(self, file, fs=0):
        self.fname = file
        self.fs = fs
        self.data = np.loadtxt(self.fname)


class ScaledPhysio(Physio):
    """Class that scales input data to [0.0, 1.0]"""

    def __init__(self, file, fs=0):
        super(ScaledPhysio,self).__init__(file,fs)

        scaler = MinMaxScaler(feature_range=(0,1))
        self.data = scaler.fit_transform(self.data.reshape(-1,1))


class FilteredPhysio(ScaledPhysio):
    """Class with filtering methods"""
    
    def __init__(self, file, fs=0):
        super(FilteredPhysio,self).__init__(file,fs)

        self.filtsig = self.data.copy()

    def reset(self):
        """Resets self.filtsig to original (scaled) data series"""
        self.filtsig = self.data.copy()

    def bandpass(self,flims):
        """Bandpass filters signal"""
        self.filtsig = bandpass_filt(self.filtsig, self.fs, flims)

    def median(self,kernel=9):
        """Median filters signal"""
        self.filtsig = median_filt(self.filtsig, kernel)


def flat_signal(signal):
    """Checks if >1D array can be flattened without data loss"""

    if signal.ndim > 1:
        if signal.shape[-1] == 1:
            signal = signal.flatten()

    return signal


def median_filt(signal,kernel):
    """Runs media filter on `signal` with window size `kernel`

    Parameters
    ----------
    signal : array-like
    kernel : int
    """

    signal = flat_signal(signal)
    if kernel%2 == 0: kernel -= 1
    
    fsig = scipy.signal.medfilt(signal,kernel_size=kernel)

    return fsig


def bandpass_filt(signal,fs,flims):
    """Runs bandpass filter on `signal` of sampling rate `fs`

    `flims` are the lower and upper bounds of the bandpass. Utilizes
    butterworth filter from scipy.signal
    
    Parameters
    ----------
    signal : array-like
    fs : float
        Samples / unit time
    flims : list-of-two
    """
    
    signal = flat_signal(signal)

    nyq_freq = fs*0.5
    nyq_cutoff = np.array(flims)/nyq_freq
    b, a = scipy.signal.butter(3, nyq_cutoff, btype='bandpass')
    fsig = scipy.signal.filtfilt(b, a, signal)
    
    return fsig