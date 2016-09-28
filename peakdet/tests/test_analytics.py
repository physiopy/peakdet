#!/usr/bin/env python

import os.path as op
import numpy as np
import pytest
import peakdet

file = op.join(op.dirname(__file__),'data','PPG.1D')

def test_HRV():
    p = peakdet.PeakFinder(file,fs=40)
    
    p.interpolate()
    p.lowpass()
    p.get_peaks()

    h = peakdet.HRV(p.rrtime, p.rrint)
    assert hasattr(h, 'rrtime')
    assert hasattr(h, 'rrint')