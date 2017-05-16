#!/usr/bin/env python

from __future__ import absolute_import
import numpy as np
from peakdet import physio


class BaseModality(physio.PeakFinder):
    def __init__(self, data, fs, TR=None):
        super(BaseModality,self).__init__(data, fs)
        self._TR = TR

    @property
    def TR(self):
        return self._TR

    @TR.setter
    def TR(self, value):
        self._TR = float(value)


class ECG(BaseModality):
    """
    Class for ECG data analysis
    """

    def __init__(self, data, fs, TR=None):
        super(ECG,self).__init__(data, fs, TR)
        self.bandpass([5.,15.])


class PPG(BaseModality):
    """
    Class for PPG data analysis
    """

    def __init__(self, data, fs, TR=None):
        super(PPG,self).__init__(data, fs, TR)
        self.lowpass([2.0])

    def get_peaks(self, thresh=0.1):
        super(PPG,self).get_peaks(thresh)

    def iHR(self, step=1, start=0, end=None):
        """
        Creates instantaneous HR time series

        Parameters
        ----------
        step : int
            How many TRs to condense into each measurement (i.e., window size)
        start : float
            Time at which to start measuring
        end : float
            Time at which to stop measuring

        Returns
        -------
        array : iHR
        """

        if self.rrint is None: return
        if end is None: end = self.rrtime[-1]

        mod   = self.TR * (step//2)
        time  = np.arange(start-mod, end+mod+1,
                          self.TR, dtype='int')
        HR    = np.zeros(len(time)-step)

        for l in range(step,len(time)):
            inds     = np.logical_and(self.rrtime>time[l-step],
                                      self.rrtime<time[l])
            relevant = self.rrint[inds]

            if relevant.size==0: continue
            HR[l-step] = (60/relevant).mean()

        return np.nan_to_num(HR)


class RESP(BaseModality):
    """
    Class for respiratory data analysis
    """

    def __init__(self, data, fs, TR=None):
        super(RESP,self).__init__(data, fs, TR)
        self.bandpass([0.01,0.5])

    def RVT(self, TR=None):
        if TR is not None: self.TR = TR
        if self.TR is None: raise ValueError('TR needs to be set!')

        peaks   = self.data[self.peakinds]
        troughs = self.data[self.troughinds]

        peak_first = self.peakinds[0] < self.troughinds[0]
        