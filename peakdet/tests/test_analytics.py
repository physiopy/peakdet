# -*- coding: utf-8 -*-

from peakdet import analytics
from peakdet.tests.utils import get_peak_data

ATTRS = [
    "rrtime",
    "rrint",
    "avgnn",
    "sdnn",
    "rmssd",
    "sdsd",
    "nn50",
    "pnn50",
    "nn20",
    "pnn20",
    "hf",
    "hf_log",
    "lf",
    "lf_log",
    "vlf",
    "vlf_log",
    "lftohf",
    "hf_peak",
    "lf_peak",
]


def test_HRV():
    peaks = get_peak_data()
    hrv = analytics.HRV(peaks)
    for attr in ATTRS:
        assert hasattr(hrv, attr)
