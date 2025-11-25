"""
Utilities for testing
"""

import sys
from os.path import join as pjoin

import numpy as np

from peakdet import io, operations
from peakdet.utils import _get_call


def get_call_func(
    arg1,
    arg2,
    *,
    kwarg1=10,
    kwarg2=20,
    exclude=None,
    serializable=True,
):
    """Test `peakdet.utils._get_call()`."""
    if exclude is None:
        exclude = ["exclude", "serializable"]
    if arg1 > 10:
        kwarg1 = kwarg1 + arg1
    if arg2 > 20:
        kwarg2 = kwarg2 + arg2
    return _get_call(exclude=exclude, serializable=serializable)


def get_test_data_path(fname=None):
    """Get `peakdet` test data path."""
    if sys.version_info >= (3, 9):
        from importlib import resources

        ref = resources.files("peakdet") / "tests/data"
        with resources.as_file(ref) as path:
            fullpath = pjoin(path, fname)
    else:
        from pkg_resources import resource_filename

        path = resource_filename("peakdet", "tests/data")
        fullpath = pjoin(path, fname)
    return fullpath if fname is not None else path


def get_sample_data():
    """Generate tiny sine wave form for testing."""
    data = np.sin(np.linspace(0, 20, 40))
    peaks, troughs = np.array([3, 15, 28]), np.array([9, 21, 34])

    return data, peaks, troughs


def get_peak_data():
    """Get some pregenerated physio data."""
    physio = io.load_physio(get_test_data_path("ECG.csv"), fs=1000)
    filt = operations.filter_physio(physio, [5.0, 15.0], "bandpass")
    peaks = operations.peakfind_physio(filt)

    return peaks
