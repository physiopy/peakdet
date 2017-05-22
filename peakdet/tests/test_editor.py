#!/usr/bin/env python

import os.path as op
import pytest
import peakdet


class Event():
    def __init__(self, step):
        self.step = step


def test_PeakEditor():
    file = op.join(op.dirname(__file__),'data','PPG.1D')
    p = peakdet.PeakFinder(file,fs=40)

    p.get_peaks()

    with pytest.raises(TypeError): peakdet.editor.PeakEditor(10,_debug=True)
    m = peakdet.editor.PeakEditor(p, _debug=True)
    m.on_span_select(10,20)
    m.undo()
    m.roll_wheel(Event(step=5))
    m.done()
