#!/usr/bin/env python

import os.path as op
import pytest
import peakdet


def test_PeakFinder():
    file = op.join(op.dirname(__file__),'data','Resp.1D')

    p = peakdet.PeakFinder(file, fs=40)
    assert p.rrint is None
    assert p.rrtime is None

    p.interpolate(10)
    p.lowpass()
    p.get_peaks()
    assert len(p.rrint) > 0
    assert len(p.rrtime) > 0
    assert len(p.peakinds) > 0
    assert len(p.peakinds)-1 == len(p.rrint)

    assert len(p.troughinds) > 0
    assert p._peaksig.shape[0] == p.peakinds.size-2

    p.plot_data(_test=True)
