#!/usr/bin/env python

import os.path as op
import numpy as np
import pytest
import peakdet

def test_PeakFinder():
    file = op.join(op.dirname(__file__),'data','Resp.1D')

    p = peakdet.PeakFinder(file, fs=40)
    assert p.rrint == []
    assert p.rrtime == []

    p.interpolate()
    p.lowpass()
    p.get_peaks(troughs=True)
    assert len(p.rrint) > 0
    assert len(p.rrtime) > 0
    assert len(p.peakinds) > 0
    assert len(p.peakinds)-1 == len(p.rrint)
    assert np.all(p.filtsig[p.peakinds] > p.filtsig.mean())

    assert len(p.troughinds) > 0
    assert np.all(p.filtsig[p.troughinds] < p.filtsig.mean())

    assert len(p._peaksig) == len(p.peakinds)
    
    p.hard_thresh()
    classes = p.classify()

    p.plot_data(_test=True)
    