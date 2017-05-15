#!/usr/bin/env python

import os.path as op
import numpy as np
import pytest
import peakdet.utils


def test_normalize():
    with pytest.raises(IndexError):
        peakdet.utils.normalize(np.random.rand(5,5))


def test_corr():
    x = np.random.rand(10)
    y = np.random.rand(9)
    peakdet.utils.corr(x, y)


def test_matchtemp():
    file = op.join(op.dirname(__file__),'data','Resp.1D')

    p = peakdet.PeakFinder(file, fs=40)
    p.get_peaks()
    peakdet.utils.match_temp(p.data, p.peakinds, p._template)
