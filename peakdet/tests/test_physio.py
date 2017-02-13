#!/usr/bin/env python

import os.path as op
import numpy as np
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


def test_FilteredPhysio():
    file = op.join(op.dirname(__file__),'data','PPG.1D')

    p1 = peakdet.FilteredPhysio(file, fs=40)
    p2 = peakdet.FilteredPhysio(file, fs=40)
    assert np.all(p2.flims == p1.flims)

    p1.bandpass()
    assert not np.all(p1.filtsig == p1.data)
    p2.bandpass([0.5,2.0])
    assert not np.all(p2.filtsig == p1.filtsig)

    for f in [p1, p2]: f.reset()
    assert np.all(p1.filtsig == p1.data)

    p1.lowpass()
    assert not np.all(p1.filtsig == p1.data)
    p2.lowpass(2.0)
    assert not np.all(p2.filtsig == p1.filtsig)

    for f in [p1, p2]: f.reset()

    p1.highpass()
    assert not np.all(p1.filtsig == p1.data)
    p2.highpass(0.5)
    assert not np.all(p2.filtsig == p1.filtsig)


def test_InterpolatedPhysio():
    file = op.join(op.dirname(__file__),'data','Resp.1D')
    data = np.loadtxt(file)

    p1 = peakdet.InterpolatedPhysio(file,fs=40)
    p2 = peakdet.FilteredPhysio(file,fs=40)

    order = 3.
    p1.interpolate(order=order)
    assert len(p1.data) > len(data)
    assert p1.fs == p2.fs * order
    assert not np.all(p1.flims == p2.flims)

    p1.reset()
    assert len(p1.data) > len(data)
    p1.reset(hard=True)
    assert len(p1.data) == len(data)

    p1.interpolate()
    assert len(p1.data) > len(data)
    assert p1.fs == p2.fs * 2.
