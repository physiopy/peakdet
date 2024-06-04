# -*- coding: utf-8 -*-

import pytest

from peakdet import external
from peakdet.tests import utils as testutils

DATA = testutils.get_test_data_path("rtpeaks.csv")


def test_load_rtpeaks(caplog):
    for channel in [1, 2, 9]:  
        hist = dict(fname=DATA, channel=channel, fs=1000.0)
        phys = external.load_rtpeaks(DATA, channel=channel, fs=1000.0)
        assert phys.history == [("load_rtpeaks", hist)]
        assert phys.fs == 1000.0
        with pytest.raises(ValueError):
            external.load_rtpeaks(
                testutils.get_test_data_path("ECG.csv"), channel=channel, fs=1000.0
            )
        assert "WARNING" in caplog.text
