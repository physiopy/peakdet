# -*- coding: utf-8 -*-

from os.path import join as pjoin
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
    fname = pjoin(testutils.get_test_data_path(), 'ECG.csv')
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


@pytest.mark.xfail
def test_new_physio_like():
    assert False


def test_get_extrema():
    # check that peak detection works
    assert_array_equal(utils.get_extrema(DATA), PEAKS)
    # check that threshold modulates detection
    assert_array_equal(utils.get_extrema(DATA, thresh=0.6), np.array([]))
    # check that trough detection works, too
    assert_array_equal(utils.get_extrema(DATA, False), TROUGHS)
    # check threshold bounds
    with pytest.raises(ValueError):
        utils.get_extrema(DATA, thresh=-0.1)
    with pytest.raises(ValueError):
        utils.get_extrema(DATA, thresh=1.1)


def test_min_peak_dist():
    # test peaks w/ and w/o removal due to `dist`
    assert_array_equal(utils.min_peak_dist(DATA, PEAKS, dist=10),
                       PEAKS)
    assert_array_equal(utils.min_peak_dist(DATA, PEAKS, dist=20),
                       np.array([3, 28]))
    # test troughs w/ and w/o removal due to `dist`
    assert_array_equal(utils.min_peak_dist(DATA, TROUGHS, False, dist=10),
                       TROUGHS)
    assert_array_equal(utils.min_peak_dist(DATA, TROUGHS, False, dist=20),
                       np.array([9, 34]))


def test_find_peaks():
    # check that `dist` parameter modulates detected peaks
    assert_array_equal(utils.find_peaks(DATA, dist=10), PEAKS)
    assert_array_equal(utils.find_peaks(DATA, dist=20), np.array([3, 28]))
    # ensure returned array is of correct type
    assert utils.find_peaks(DATA).dtype == np.int64


def test_find_troughs():
    # check that `dist` parameter modulates detected troughs
    assert_array_equal(utils.find_troughs(DATA, dist=10), TROUGHS)
    assert_array_equal(utils.find_troughs(DATA, dist=20), np.array([9, 34]))
    # ensure returned array is of correct type
    assert utils.find_peaks(DATA).dtype == np.int64


def test_check_troughs():
    true = np.array([9, 21])
    # check that func fills in when no troughs provided
    assert_array_equal(utils.check_troughs(DATA, PEAKS, []), true)
    # check that func disregard troughs outside of peak bounds
    assert_array_equal(utils.check_troughs(DATA, PEAKS, TROUGHS), true)
    # check that func removes when two points are "troughs" inside peaks
    assert_array_equal(utils.check_troughs(DATA, PEAKS, np.array([9, 10, 21])),
                       true)


@pytest.mark.xfail
def test_gen_temp():
    assert False


def test_corr():
    x = np.random.rand(10, 1)
    # works both as 2D and 1D vectors (i.e., squeezeable)
    assert np.allclose(utils.corr(x, x), 1)
    assert np.allclose(utils.corr(x.squeeze(), x.squeeze()), 1)
    # error raised when inputs aren't the same size
    with pytest.raises(ValueError):
        utils.corr(x, np.random.rand(9, 1))
    # error raised when one of the inputs is not squeezeable
    with pytest.raises(ValueError):
        utils.corr(x, np.random.rand(10, 2))
    # zscore only first
    utils.corr(x, x, zscored=[False, True])
    # zscore only second
    utils.corr(x, x, zscored=[True, False])
    # zscore both
    utils.corr(x, x, zscored=[True, True])


@pytest.mark.xfail
def test_corr_template():
    assert False


@pytest.mark.xfail
def test_match_temp():
    assert False
