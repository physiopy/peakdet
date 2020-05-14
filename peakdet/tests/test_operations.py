# -*- coding: utf-8 -*-

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from peakdet import operations
from peakdet.physio import Physio
from peakdet.tests import utils as testutils

data = np.loadtxt(testutils.get_test_data_path('ECG.csv'))
WITHFS = Physio(data, fs=1000.)
NOFS = Physio(data)


def test_filter_physio():
    # check lowpass and highpass filters
    for meth in ['lowpass', 'highpass']:
        params = dict(cutoffs=2, method=meth)
        assert len(WITHFS) == len(operations.filter_physio(WITHFS, **params))
        params['order'] = 5
        assert len(WITHFS) == len(operations.filter_physio(WITHFS, **params))
        params['cutoffs'] = [2, 10]
        with pytest.raises(ValueError):
            operations.filter_physio(WITHFS, **params)
        with pytest.raises(ValueError):
            operations.filter_physio(NOFS, **params)
    # check bandpass and bandstop filters
    for meth in ['bandpass', 'bandstop']:
        params = dict(cutoffs=[2, 10], method=meth)
        assert len(WITHFS) == len(operations.filter_physio(WITHFS, **params))
        params['order'] = 5
        assert len(WITHFS) == len(operations.filter_physio(WITHFS, **params))
        params['cutoffs'] = 2
        with pytest.raises(ValueError):
            operations.filter_physio(WITHFS, **params)
        with pytest.raises(ValueError):
            operations.filter_physio(NOFS, **params)
    # check appropriate filter methods
    with pytest.raises(ValueError):
        operations.filter_physio(WITHFS, 2, 'notafilter')
    # check nyquist
    with pytest.raises(ValueError):
        operations.filter_physio(WITHFS, [2, 1000], 'bandpass')


def test_interpolate_physio():
    with pytest.raises(ValueError):
        operations.interpolate_physio(NOFS, 100.)
    for fn in [50, 100, 200, 500, 2000, 5000]:
        new = operations.interpolate_physio(WITHFS, fn)
        assert new.fs == fn
        if fn < WITHFS.fs:
            assert len(new) < len(WITHFS)
        else:
            assert len(new) > len(WITHFS)


def test_peakfind_physio():
    with pytest.raises(ValueError):
        operations.peakfind_physio(NOFS)
    operations.peakfind_physio(NOFS, dist=20)
    operations.peakfind_physio(NOFS, thresh=0.4, dist=20)
    operations.peakfind_physio(WITHFS)
    operations.peakfind_physio(WITHFS, dist=20)
    operations.peakfind_physio(WITHFS, thresh=0.4)


def test_delete_peaks():
    to_delete = [24685, 44169]
    peaks = operations.peakfind_physio(WITHFS)
    deleted = operations.delete_peaks(peaks, to_delete)
    assert len(deleted.peaks) == len(peaks.peaks) - len(to_delete)


def test_reject_peaks():
    to_reject = [24685, 44169]
    peaks = operations.peakfind_physio(WITHFS)
    rejected = operations.reject_peaks(peaks, to_reject)
    assert len(rejected.peaks) == len(peaks.peaks) - len(to_reject)


def test_edit_physio():
    # value error when no sampling rate provided for interactive editing
    with pytest.raises(ValueError):
        operations.edit_physio(NOFS)
    # if sampling rate provided but no peaks/troughs just return
    operations.edit_physio(WITHFS)


def test_plot_physio():
    for data in [NOFS, WITHFS]:
        assert isinstance(operations.plot_physio(data), matplotlib.axes.Axes)
    peaks = operations.peakfind_physio(WITHFS)
    assert isinstance(operations.plot_physio(peaks), matplotlib.axes.Axes)
    fig, ax = plt.subplots(1, 1)
    assert ax == operations.plot_physio(peaks, ax=ax)
