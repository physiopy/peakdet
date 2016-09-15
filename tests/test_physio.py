#!/usr/bin/env python

import os.path as op
import numpy as np
import pytest
from peakdet import Physio

def test_PhysioClass():
    file = op.join(op.dirname(__file__),'data','ECG1.1D')
    data = np.loadtxt(file)

    p = Physio(file)

    assert p.fname == file
    assert np.all(p.data == data)