# -*- coding: utf-8 -*-

import pytest
from peakdet import editor
from peakdet.tests.utils import get_peak_data

PEAKS = get_peak_data()


@pytest.mark.xfail
def test_PhysioEditor():
    assert False


def test_delete_peaks():
    to_delete = [82, 24682, 44166]
    deleted = editor.delete_peaks(PEAKS, to_delete, copy=True)[0]
    assert len(deleted.peaks) == len(PEAKS.peaks) - len(to_delete)


def test_reject_peaks():
    to_reject = [82, 24682, 44166]
    rejected = editor.reject_peaks(PEAKS, to_reject, copy=True)[0]
    assert len(rejected.peaks) == len(PEAKS.peaks) - len(to_reject)
