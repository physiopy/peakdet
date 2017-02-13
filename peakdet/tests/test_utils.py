#!/usr/bin/env python

import numpy as np
import pytest
import peakdet.utils


def test_normalize():
    with pytest.raises(IndexError):
        peakdet.utils.normalize(np.random.rand(5,5))
