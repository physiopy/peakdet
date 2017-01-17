#!/usr/bin/env python

import numpy as np
import pytest
import peakdet.utils

def test_comp_peaks():
    with pytest.raises(TypeError):
        peakdet.utils.comp_peaks(np.random.rand(10),np.random.rand(10),comparator=np.mean)
    