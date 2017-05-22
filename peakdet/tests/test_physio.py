#!/usr/bin/env python

import os.path as op
import numpy as np
import matplotlib.pyplot as plt
import pytest
import peakdet


def test_Physio():
    file = op.join(op.dirname(__file__),'data','PPG.1D')
    data = np.loadtxt(file)

    p = peakdet.Physio(file, fs=40)
    assert p._dinput == file
    assert p.fs == 40.
    assert np.all(p.rawdata == data)

    p = peakdet.Physio(data, fs=40)
    assert np.all(p.rawdata == data)
    p.fs = 10.
    assert p.fs == 10.

    p = peakdet.Physio(40,fs=40.)
    with pytest.raises(TypeError): p.rawdata

    file = op.join(op.dirname(__file__),'data','header.1D')
    p = peakdet.Physio(file,fs=40.)
    assert np.all(p.rawdata == np.loadtxt(file,skiprows=1))


def test_ScaledPhysio():
    file = op.join(op.dirname(__file__),'data','PPG.1D')

    p = peakdet.ScaledPhysio(file, fs=40)
    p.data
    p.data = np.loadtxt(file)


def test_FilteredPhysio():
    file = op.join(op.dirname(__file__),'data','PPG.1D')

    p1 = peakdet.FilteredPhysio(file, fs=40)
    p2 = peakdet.FilteredPhysio(file, fs=40)
    assert np.all(p2._flims == p1._flims)

    p1.bandpass()
    p2.bandpass([0.5,2.0])
    assert not np.all(p2.data == p1.data)

    for f in [p1, p2]: f.reset()

    p1.lowpass()
    p2.lowpass(2.0)
    assert not np.all(p2.data == p1.data)

    for f in [p1, p2]: f.reset()

    p1.highpass()
    p2.highpass(0.5)
    assert not np.all(p2.data == p1.data)


def test_InterpolatedPhysio():
    file = op.join(op.dirname(__file__),'data','Resp.1D')
    data = np.loadtxt(file)

    p1 = peakdet.InterpolatedPhysio(file,fs=40)
    p2 = peakdet.FilteredPhysio(file,fs=40)

    order = 3.
    p1.interpolate(order=order)
    assert len(p1.data) > len(data)
    assert p1.fs == p2.fs * order
    assert not np.all(p1._flims == p2._flims)

    p1.reset()
    assert len(p1.data) > len(data)

    p1.reset(hard=True)
    assert len(p1.data) == len(data)

    p1.interpolate()
    assert len(p1.data) > len(data)
    assert p1.fs == p2.fs * 2.


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
    assert len(p._template) > 0
    assert len(p.time) == len(p.data)

    assert len(p.troughinds) > 0
    assert p._peaksig.shape[0] == p.peakinds.size-2
    fig = p.plot(_debug=True)
    plt.close(fig)
