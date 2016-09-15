#!/usr/bin/env python

import os
import numpy as np
import scipy.signal

class Physio():
    """Class to handle an instance of physiological data"""

    def __init__(self, file, fs=None):
        self.fname = file

        if fs: self.fs = fs

        try: self.data = np.loadtxt(file)
        except: self.data = np.loadtxt(file,delimiter=',')

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

    Returns
    -------
    array : bandpassed signal
    """
    
    nyq_freq = fs*0.5
    nyq_cutoff = np.array(flims)/nyq_freq
    b, a = scipy.signal.butter(3, nyq_cutoff, btype='bandpass')
    filtSig = scipy.signal.filtfilt(b, a, signal)
    
    return filtSig