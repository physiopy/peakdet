# -*- coding: utf-8 -*-

import numpy as np
from numpy.testing import assert_array_equal
import pytest
from peakdet import physio, utils
from peakdet.tests import utils as testutils

DATA, PEAKS, TROUGHS = testutils.get_sample_data()
GET_CALL_ARGUMENTS = [
    # check basic functionality
    dict(
        function='get_call_func',
        input=dict(
            arg1=1, arg2=2, serializable=False
        ),
        expected=dict(
            arg1=1, arg2=2, kwarg1=10, kwarg2=20
        )
    ),
    # check that changing kwargs in function persists to output
    dict(
        function='get_call_func',
        input=dict(
            arg1=11, arg2=21, serializable=False
        ),
        expected=dict(
            arg1=11, arg2=21, kwarg1=21, kwarg2=41
        )
    ),
    # confirm serializability is effective
    dict(
        function='get_call_func',
        input=dict(
            arg1=1, arg2=2, kwarg1=np.array([1, 2, 3]), serializable=True
        ),
        expected=dict(
            arg1=1, arg2=2, kwarg1=[1, 2, 3], kwarg2=20
        )
    ),
]


def test_get_call():
    for entry in GET_CALL_ARGUMENTS:
        fcn, args = testutils.get_call_func(**entry['input'])
        assert fcn == entry['function']
        assert args == entry['expected']


def test_check_physio():
    fname = testutils.get_test_data_path('ECG.csv')
    data = physio.Physio(np.loadtxt(fname), fs=1000.)
    # check that `ensure_fs` is functional
    with pytest.raises(ValueError):
        utils.check_physio(fname)
    assert isinstance(utils.check_physio(fname, False), physio.Physio)
    # "normal" instance should just pass
    assert isinstance(utils.check_physio(data), physio.Physio)
    # check that copy works
    assert utils.check_physio(data) == data
    assert utils.check_physio(data, copy=True) != data


def test_new_physio_like():
    fname = testutils.get_test_data_path('ECG.csv')
    data = physio.Physio(np.loadtxt(fname), fs=1000.)
    data._history = [('does history', 'copy?')]
    data._metadata['peaks'] = np.array([1, 2, 3])
    # assert all copies happen by default
    new_data = utils.new_physio_like(data, data[:])
    assert np.allclose(data, utils.new_physio_like(data, data[:]))
    assert new_data.fs == data.fs
    assert new_data.data.dtype == data.data.dtype
    assert new_data.history == data.history
    assert new_data._metadata == data._metadata
    # check if changes apply
    new_data = utils.new_physio_like(data, data[:], fs=50, dtype=int,
                                     copy_history=False, copy_metadata=False)
    assert np.allclose(data, utils.new_physio_like(data, data[:]))
    assert new_data.fs == 50
    assert new_data.data.dtype == int
    assert new_data.history == []
    for k, v in new_data._metadata.items():
        assert v.size == 0


def test_check_troughs():
    true = np.array([9, 21])
    assert_array_equal(utils.check_troughs(DATA, PEAKS), true)
