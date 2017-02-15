#!/usr/bin/env python

import numpy as np
from . import physio
from . import utils


class ECG(physio.PeakFinder):
    """Class for ECG data analysis"""
    def __init__(self, data, fs):
        super(ECG,self).__init__(data, fs)


class PPG(physio.PeakFinder):
    """Class for PPG data analysis"""
    def __init__(self, data, fs):
        super(PPG,self).__init__(data, fs)


class RESP(physio.PeakFinder):
    """Class for respiratory data analysis"""
    def __init__(self, data, fs):
        super(RESP,self).__init__(data, fs)
