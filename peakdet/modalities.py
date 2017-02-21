#!/usr/bin/env python

from __future__ import absolute_import
import numpy as np
from peakdet import physio
from peakdet import utils


class ECG(physio.PeakFinder):
    """
    Class for ECG data analysis
    """

    def __init__(self, data, fs):
        super(ECG,self).__init__(data, fs)
        self.bandpass([5.,15.])


class PPG(physio.PeakFinder):
    """
    Class for PPG data analysis
    """

    def __init__(self, data, fs):
        super(PPG,self).__init__(data, fs)
        self.lowpass([2.0])


class RESP(physio.PeakFinder):
    """
    Class for respiratory data analysis
    """

    def __init__(self, data, fs):
        super(RESP,self).__init__(data, fs)
        self.lowpass([0.5])
