# -*- coding: utf-8 -*-

import pytest
from sklearn.utils import Bunch
from peakdet import editor
from peakdet.tests.utils import get_peak_data

PEAKS = get_peak_data()


def test_PhysioEditor():
    edits = editor._PhysioEditor(get_peak_data())
    # test scroll functionality
    edits.on_wheel(Bunch(step=10))
    # test reject / delete functionality
    for m in range(2):
        edits.on_reject(0, 10)
        edits.on_delete(10, 20)
    # undo delete + reject
    for m in range(2):
        edits.undo()
    # test key undo (and undo when history doesn't exist)
    edits.on_key(Bunch(key='ctrl+z'))
    # redo so that there is history on quit
    edits.on_reject(0, 10)
    edits.on_delete(10, 20)
    # quit editor and clean up edits
    edits.on_key(Bunch(key='ctrl+q'))

    with pytest.raises(TypeError):
        editor._PhysioEditor([0, 1, 2])


def test_delete_peaks():
    to_delete = [82, 24682, 44166]
    deleted = editor.delete_peaks(PEAKS, to_delete, copy=True)[0]
    assert len(deleted.peaks) == len(PEAKS.peaks) - len(to_delete)


def test_reject_peaks():
    to_reject = [82, 24682, 44166]
    rejected = editor.reject_peaks(PEAKS, to_reject, copy=True)[0]
    assert len(rejected.peaks) == len(PEAKS.peaks) - len(to_reject)
