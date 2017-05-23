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
        """
        Repetition time
        """

        return self._TR

    @TR.setter
    def TR(self, value):
        self._TR = float(value)


class HRModality():
    """
    Class that supplies ECG/PPG with common heart rate functions
    """

    def iHR(self, step=1, start=0, end=None, TR=None):
        """
        Creates instantaneous HR time series

        Parameters
        ----------
        step : int
            how many TRs to condense into each measurement (i.e., window size)
        start : float
            time at which to start measuring
        end : float
            time at which to stop measuring
       TR : float
            repetition time

        Returns
        -------
        array : iHR
        """

        if TR is not None: self.TR = TR
        if self.TR is None:
            raise ValueError("Need to set TR in order to get iHR time series.")
        if self.rrint is None: return
        if end is None: end = self.rrtime[-1]

        mod   = self.TR * (step//2)
        time  = np.arange(start-mod, end+mod+1,
                          self.TR, dtype='int')
        HR    = np.zeros(len(time)-step)

        for l in range(step,time.size):
            inds     = np.logical_and(self.rrtime>time[l-step],
                                      self.rrtime<time[l])
            relevant = self.rrint[inds]

            if relevant.size==0: continue
            HR[l-step] = (60/relevant).mean()

        return HR

    def meanHR(self):
        return (60/np.diff(self.peakinds)).mean()/self.fs


class ECG(BaseModality, HRModality):
    """
    Class for ECG data analysis

    Bandpass filters data (5-15Hz) by default
    """

    def __init__(self, data, fs, TR=None):
        super(ECG,self).__init__(data, fs, TR)
        self.bandpass([5.,15.])

    def reset(self, hard=False):
        """
        Removes manual filtering and peak-finding from data

        Default class filtering (i.e., from peakdet.ECG) is not removed

        Parameters
        ----------
        hard : bool (False)
            also remove interpolation from data
        """

        super(ECG,self).reset(hard=hard)
        self.bandpass([5.,15.])


class PPG(BaseModality, HRModality):
    """
    Class for PPG data analysis

    Lowpass filters data (2Hz) by default
    """

    def __init__(self, data, fs, TR=None):
        super(PPG,self).__init__(data, fs, TR)
        self.lowpass([2.0])

    def reset(self, hard=False):
        """
        Removes manual filtering and peak-finding from data

        Default class filtering (i.e., from peakdet.PPG) is not removed

        Parameters
        ----------
        hard : bool (False)
            also remove interpolation from data
        """

        super(PPG,self).reset(hard=hard)
        self.lowpass([2.0])

    def get_peaks(self, thresh=0.1):
        super(PPG,self).get_peaks(thresh)


class RESP(BaseModality):
    """
    Class for respiratory data analysis

    Bandpass filters data (0.05-0.5Hz) by default
    """

    def __init__(self, data, fs, TR=None):
        super(RESP,self).__init__(data, fs, TR)
        self.bandpass([0.05,0.5])

    def reset(self, hard=False):
        """
        Removes manual filtering and peak-finding from data

        Default class filtering (i.e., from peakdet.RESP) is not removed

        Parameters
        ----------
        hard : bool (False)
            also remove interpolation from data
        """

        super(RESP,self).reset(hard=hard)
        self.bandpass([0.05,0.5])

    def RVT(self, start=0, end=None, TR=None):
        """
        Creates respiratory volume time series (interpolated to TR)

        Steps for which no RVT data exist will be replaced by the average RVT
        signal.

        Parameters
        ----------
        start : float
            time at which to start measuring
        end : float
            time at which to stop measuring
        TR : float
            repetition time

        Returns
        -------
        array : RVT
        """

        if TR is not None: self.TR = TR
        if self.TR is None:
            raise ValueError("Need to set TR in order to get RVT time series.")
        if self.rrint is None: return
        if end is None: end = self.rrtime[-1]

        pheight, theight = self.data[self.peakinds], self.data[self.troughinds]
        rvt = (pheight[:-1]-theight) / (np.diff(self.peakinds)/self.fs)
        rt  = (self.peakinds/self.fs)[1:]

        time = np.arange(start, end+1, self.TR, dtype='int')
        iRVT = np.interp(time, rt, rvt, left=rvt.mean(), right=rvt.mean())

        return iRVT
