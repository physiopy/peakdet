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


def test_edit_physio():
    # value error when no sampling rate provided for interactive editing
    with pytest.raises(ValueError):
        operations.edit_physio(NOFS)
    # don't error if not interactive editing
    nofs_peaks = operations.peakfind_physio(NOFS, dist=250)
    operations.edit_physio(nofs_peaks,
                           delete=nofs_peaks.peaks[:2],
                           reject=nofs_peaks.peaks[-2:])
    operations.edit_physio(WITHFS)
    withfs_peaks = operations.peakfind_physio(WITHFS)
    operations.edit_physio(withfs_peaks,
                           delete=withfs_peaks.peaks[:2],
                           reject=withfs_peaks.peaks[-2:])


def test_plot_physio():
    for data in [NOFS, WITHFS]:
        assert isinstance(operations.plot_physio(data), matplotlib.axes.Axes)
    peaks = operations.peakfind_physio(WITHFS)
    assert isinstance(operations.plot_physio(peaks), matplotlib.axes.Axes)
    fig, ax = plt.subplots(1, 1)
    assert ax == operations.plot_physio(peaks, ax=ax)
