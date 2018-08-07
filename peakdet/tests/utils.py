"""
Utilities for testing
"""

from os.path import join, dirname
from peakdet.utils import _get_call


def get_call_func(arg1, arg2, *, kwarg1=10, kwarg2=20,
                  exclude=[], serializable=True):
    """ Function for testing `peakdet.utils._get_call()` """
    if arg1 > 10:
        kwarg1 = kwarg1 + arg1
    if arg2 > 20:
        kwarg2 = kwarg2 + arg2
    return _get_call(exclude=exclude, serializable=serializable)


def get_test_data_path():
    """ Function for getting `peakdet` test data path """
    return join(dirname(__file__), 'data')
