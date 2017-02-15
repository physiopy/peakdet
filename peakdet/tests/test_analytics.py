#!/usr/bin/env python

import os.path as op
import pytest
import peakdet


def test_HRV():
    file = op.join(op.dirname(__file__),'data','PPG.1D')
    p = peakdet.PeakFinder(file,fs=40)

    p.interpolate()
    p.lowpass()
    p.get_peaks()

    h = peakdet.HRV(p.rrtime, p.rrint)

    attrs = ['_rrtime', '_rrint', '_irri', '_sd', '_fft', 'avgnn',
             'sdnn', 'rmssd', 'sdsd', 'nn50', 'pnn50', 'nn20', 'pnn20',
             '_hf', '_lf', '_vlf', 'hf', 'hf_log', 'lf', 'lf_log',
             'vlf', 'vlf_log', 'lftohf', 'hf_peak', 'lf_peak']

    for a in attrs: assert hasattr(h,a)
