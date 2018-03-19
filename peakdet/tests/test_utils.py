#!/usr/bin/env python

import os.path as op
import numpy as np
import pytest
import peakdet


def test_saveload(tmpdir):
    fname = tmpdir.join('output')
    data = np.random.rand(100)
    to_save = peakdet.PeakFinder(data, 40)
    peakdet.utils.save(fname.strpath, to_save)
    loaded = peakdet.utils.load(fname.strpath)

    assert isinstance(loaded, peakdet.PeakFinder)
    assert np.allclose(to_save.data, loaded.data)


def test_normalize():
    with pytest.raises(IndexError):
        peakdet.utils.normalize(np.random.rand(5, 5))


def test_corr():
    x = np.random.rand(10)
    y = np.random.rand(9)
    peakdet.utils.corr(x, y)


def test_corrtemp():
    np.random.seed(10)
    p = peakdet.PeakFinder(np.sin(np.arange(100)), fs=1)
    p.get_peaks(thresh=0.2)
    assert len(p._template) > 0


def test_matchtemp():
    fname = op.join(op.dirname(__file__), 'data', 'PPG.1D')

    p = peakdet.PeakFinder(fname, fs=40)
    p.get_peaks()
    peakdet.utils.match_temp(p.data, p.peakinds, p._template)

    data = np.loadtxt(fname)
    data = data[:500]
    p = peakdet.PeakFinder(data, fs=40)
    p.get_peaks()
    peakdet.utils.match_temp(p.data, p.peakinds, p._template)
