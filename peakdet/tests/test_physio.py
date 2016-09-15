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

    assert p.fname == file
    assert p.fs == 40.
    
    assert p.data.max() <= 1.0
    assert p.data.min() >= 0.0
    assert len(p.data) == len(data)


def test_FilteredPhysio():
    p = peakdet.FilteredPhysio(file, fs=40)

    p.bandpass([0.5,2.0])
    assert len(p.filtsig) == len(p.data)
    assert not np.all(p.filtsig == p.data)

    p.reset()
    assert np.all(p.filtsig == p.data)

    p.median(kernel=12)
    assert len(p.filtsig) == len(p.data)
    assert not np.all(p.filtsig == p.data)