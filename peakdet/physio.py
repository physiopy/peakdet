#!/usr/bin/env python

import os
import numpy as np
import scipy.signal
from scipy.interpolate import InterpolatedUnivariateSpline
from sklearn.preprocessing import MinMaxScaler
from .utils import *

class Physio(object):
    """Class to handle an instance of physiological data"""

    def __init__(self, data, fs):
        self._fs = float(fs)
        self._dinput = data

    @property
    def fs(self):
        return self._fs

    @fs.setter
    def fs(self, value):
        self._fs = float(value)

    @property
    def rawdata(self):
        if isinstance(self._dinput, (str)):
            try: return np.loadtxt(self._dinput)
            except ValueError: return np.loadtxt(self._dinput,skiprows=1)
        elif isinstance(self._dinput, (np.ndarray,list)):
            return np.asarray(self._dinput)
        else:
            raise TypeError("Data input must be filename or array-like.")


class ScaledPhysio(Physio):
    """Class that scales input data to [0.0, 1.0]"""

    def __init__(self, data, fs):
        super(ScaledPhysio,self).__init__(data,fs)
        scaler = MinMaxScaler(feature_range=(0,1))
        self._data = scaler.fit_transform(self.rawdata.reshape(-1,1))

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = np.asarray(value)


class FilteredPhysio(ScaledPhysio):
    """Class with bandpass filter method"""
    
    def __init__(self, data, fs):
        super(FilteredPhysio,self).__init__(data,fs)
        self._filtsig = self.data.copy()

    @property
    def flims(self):
        return gen_flims(self.data, self.fs)

    @property
    def filtsig(self):
        return self._filtsig

    def reset(self):
        """Resets self.filtsig to original (scaled) data series"""
        self._filtsig = self.data.copy()

    def bandpass(self, flims=None):
        """Bandpass filters signal"""
        if not flims: flims = self.flims
        self._filtsig = bandpass_filt(self._filtsig, self.fs, flims)

    def lowpass(self, flims=None):
        """Lowpass filters signal"""
        if not flims: flims = self.flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[-1]
        self._filtsig = bandpass_filt(self._filtsig, self.fs, flims, btype='low')

    def highpass(self, flims=None):
        """Highpass filters signal"""
        if not flims: flims = self.flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[0]
        self._filtsig = bandpass_filt(self._filtsig, self.fs, flims, btype='high')


class InterpolatedPhysio(FilteredPhysio):
    """Class with interpolation method"""

    def __init__(self, data, fs):
        super(InterpolatedPhysio,self).__init__(data,fs)
        self._rawfs = self.fs

    def interpolate(self, order=2):
        """Interpolates data to `order` * `fs`"""
        t = np.arange(0, self.data.size/self.fs, 1./self.fs)
        tn = np.arange(0, t[-1], 1./(self.fs*order))
        i = InterpolatedUnivariateSpline(t,self.data)

        self.data, self.fs = i(tn), self.fs*order
        self.reset()

    def reset(self, hard=False):
        if hard:
            super(InterpolatedPhysio,self).__init__(self._dinput,self._rawfs)
        else:
            super(InterpolatedPhysio,self).reset()


class PeakFinder(InterpolatedPhysio):
    """Class with peak (and trough) finding method(s)"""

    def __init__(self, data, fs):
        super(PeakFinder,self).__init__(data, fs)
        self._peakinds = []
        self._troughinds = []

    @property
    def rrtime(self):
        if len(self.peakinds): 
            return self._peakinds[1:]/self.fs
        else: 
            return []

    @property
    def rrint(self):
        if len(self.peakinds): 
            return (self.peakinds[1:] - self.peakinds[:-1])/self.fs
        else: 
            return []

    @property
    def peakinds(self):
        return self._peakinds

    @property
    def troughinds(self):
        return self._troughinds

    def get_peaks(self, order=2, troughs=False):
        filt_inds = scipy.signal.argrelmax(self.filtsig,order=order)[0]
        raw_inds = scipy.signal.argrelmax(self.data,order=order)[0]

        inds = raw_inds[comp_lists(filt_inds, raw_inds)]
        self._peakinds = inds[self.filtsig[inds] > self.filtsig.mean()]

        if troughs: self.get_troughs()

    def get_troughs(self, order=2):
        if not hasattr(self,'peakinds'): self.get_peaks()

        filt_inds = scipy.signal.argrelmin(self.filtsig,order=order)[0]
        raw_inds = scipy.signal.argrelmin(self.data,order=order)[0]

        inds = raw_inds[comp_lists(filt_inds, raw_inds)]
        self._troughinds = inds[self.filtsig[inds] < self.filtsig.mean()]