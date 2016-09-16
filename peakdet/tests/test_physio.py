#!/usr/bin/env python

import os.path as op
import numpy as np
import pytest
import peakdet  

file = op.join(op.dirname(__file__),'data','PPG.1D')
data = np.loadtxt(file)

def test_Physio():
    p = peakdet.Physio(file, fs=40)

    assert p.fname == file
    assert p.fs == 40.
    assert np.all(p.data == data)


def test_ScaledPhysio():
    p = peakdet.ScaledPhysio(file, fs=40)

    assert p.data.max() <= 1.0
    assert p.data.min() >= 0.0


def test_FilteredPhysio():
    p1 = peakdet.FilteredPhysio(file, fs=40)
    p2 = peakdet.FilteredPhysio(file, fs=40)
    assert (p2.flims == p1.flims)

    p1.bandpass()
    assert not np.all(p1.filtsig == p1.data)
    p2.bandpass([0.5,2.0])
    assert not np.all(p2.filtsig == p1.filtsig)

    p1.reset()
    p2.reset()
    assert np.all(p1.filtsig == p1.data)

    p1.lowpass()
    assert not np.all(p1.filtsig == p1.data)
    p2.lowpass(0.5)
    assert not np.all(p2.filtsig == p1.filtsig)


file = op.join(op.dirname(__file__),'data','Resp.1D')
data = np.loadtxt(file)

def test_InterpolatedPhysio():
    p1 = peakdet.InterpolatedPhysio(file,fs=40)
    p2 = peakdet.FilteredPhysio(file,fs=40)

    assert len(p1.data) > len(data)
    assert p1.fs == 40. * 2.
    assert not np.all(p1.flims == p2.flims)