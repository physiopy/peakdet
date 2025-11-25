"""
Various utilities for processing physiological data.

These should not be called directly but should support wrapper functions stored in
`peakdet.operations`.
"""

import inspect
import sys
from functools import wraps

import numpy as np
from loguru import logger

from peakdet import physio


def make_operation(*, exclude=None):
    """
    Wrap functions into Physio operations.

    Wrapped functions should accept a :class:`peakdet.Physio` instance, `data`,
    as their first parameter, and should return a :class:`peakdet.Physio`
    instance

    Parameters
    ----------
    exclude : list, optional
        What function parameters to exclude from being stored in history.
        Default: 'data'
    """

    def get_call(func):
        @wraps(func)
        def wrapper(data, *args, **kwargs):
            # exclude 'data', by default
            ignore = ["data"] if exclude is None else exclude

            # grab parameters from `func` by binding signature
            name = func.__name__
            sig = inspect.signature(func)
            params = sig.bind(data, *args, **kwargs).arguments

            # actually run function on data
            data = func(data, *args, **kwargs)

            # it shouldn't be, but don't bother appending to history if it is
            if data is None:
                return data

            # get parameters and sort by key name, dropping ignored items and
            # attempting to coerce any numpy arrays or pandas dataframes (?!)
            # into serializable objects; this isn't foolproof but gets 80% of
            # the way there
            provided = {k: params[k] for k in sorted(params.keys()) if k not in ignore}
            for k, v in provided.items():
                if hasattr(v, "tolist"):
                    provided[k] = v.tolist()

            # append everything to data instance history
            data._history += [(name, provided)]

            return data

        return wrapper

    return get_call


def _get_call(*, exclude=None, serializable=True):
    """
    Return calling function name and dict of provided arguments (name : value).

    Parameters
    ----------
    exclude : list, optional
        What arguments to exclude from provided argument : value dictionary.
        Default: ['data']
    serializable : bool, optional
        Whether to coerce argument values to JSON serializable form. Default:
        True

    Returns
    -------
    function: str
        Name of calling function
    provided : dict
        Dictionary of function arguments and provided values
    """
    exclude = ["data"] if exclude is None else exclude
    if not isinstance(exclude, list):
        exclude = [exclude]

    # get one function call up the stack (the bottom is _this_ function)
    calling = inspect.stack(0)[1]
    frame, function = calling.frame, calling.function

    # get all the args / kwargs from the calling function
    argspec = inspect.getfullargspec(frame.f_globals[function])
    args = sorted(argspec.args + argspec.kwonlyargs)

    # save arguments + argument values for everything not in `exclude`
    provided = {k: frame.f_locals[k] for k in args if k not in exclude}

    # if we want `provided` to be serializable, we can do a little cleaning up
    # this is NOT foolproof, but will coerce numpy arrays to lists which tends
    # to be the main issue with these sorts of things
    if serializable:
        for k, v in provided.items():
            if hasattr(v, "tolist"):
                provided[k] = v.tolist()

    return function, provided


def check_physio(data, ensure_fs=True, copy=False):
    """
    Check that `data` is in correct format (i.e., `peakdet.Physio`).

    Parameters
    ----------
    data : Physio_like
    ensure_fs : bool, optional
        Raise ValueError if `data` does not have a valid sampling rate
        attribute.
    copy: bool, optional
        Whether to return a copy of the provided data. Default: False

    Returns
    -------
    data : peakdet.Physio
        Loaded physio object

    Raises
    ------
    ValueError
        If `ensure_fs` is set and `data` doesn't have valid sampling rate
    """
    from peakdet.io import load_physio

    if not isinstance(data, physio.Physio):
        data = load_physio(data)
    if ensure_fs and np.isnan(data.fs):
        raise ValueError("Provided data does not have valid sampling rate.")
    if copy is True:
        return new_physio_like(
            data, data.data, copy_history=True, copy_metadata=True, copy_suppdata=True
        )
    return data


def new_physio_like(
    ref_physio,
    data,
    *,
    fs=None,
    suppdata=None,
    dtype=None,
    copy_history=True,
    copy_metadata=True,
    copy_suppdata=True,
):
    """
    Make `data` into physio object like `ref_data`.

    Parameters
    ----------
    ref_physio : Physio_like
        Reference `Physio` object
    data : array_like
        Input physiological data
    fs : float, optional
        Sampling rate of `data`. If not supplied, assumed to be the same as
        in `ref_physio`
    suppdata : array_like, optional
        New supplementary data. If not supplied, assumed to be the same.
    dtype : data_type, optional
        Data type to convert `data` to, if conversion needed. Default: None
    copy_history : bool, optional
        Copy history from `ref_physio` to new physio object. Default: True
    copy_metadata : bool, optional
        Copy metadata from `ref_physio` to new physio object. Default: True
    copy_suppdata : bool, optional
        Copy suppdata from `ref_physio` to new physio object. Default: True

    Returns
    -------
    data : peakdet.Physio
        Loaded physio object with provided `data`
    """
    if fs is None:
        fs = ref_physio.fs
    if dtype is None:
        dtype = ref_physio.data.dtype
    history = list(ref_physio.history) if copy_history else []
    metadata = dict(**ref_physio._metadata) if copy_metadata else None

    if suppdata is None:
        suppdata = ref_physio._suppdata if copy_suppdata else None

    # make new class
    out = ref_physio.__class__(
        np.array(data, dtype=dtype),
        fs=fs,
        history=history,
        metadata=metadata,
        suppdata=suppdata,
    )
    return out


def check_troughs(data, peaks, troughs=None):
    """
    Confirm that `troughs` exists between every set of `peaks` in `data`.

    Parameters
    ----------
    data : array-like
        Input data for which `troughs` and `peaks` were detected
    peaks : array-like
        Indices of suspected peak locations in `data`
    troughs : array-like or None, optional
        Indices of suspected troughs locations in `data`, if any.

    Returns
    -------
    troughs : np.ndarray
        Indices of trough locations in `data`, dependent on `peaks`
    """
    # If there's a trough after all peaks, keep it.
    if troughs is not None and troughs[-1] > peaks[-1]:
        all_troughs = np.zeros(peaks.size, dtype=int)
        assert all_troughs[-1] == troughs[-1]
    else:
        all_troughs = np.zeros(peaks.size - 1, dtype=int)

    for f in range(peaks.size - 1):
        dp = data[peaks[f] : peaks[f + 1]]

        if dp.size > 0:
            idx = peaks[f] + np.argwhere(dp == dp.min())[0]
            all_troughs[f] = idx

    return all_troughs


def enable_logger(loglevel="INFO", diagnose=True, backtrace=True):
    """
    Toggle the use of the module's logger and configures it.

    Parameters
    ----------
    loglevel : {'INFO', 'DEBUG', 'WARNING', 'ERROR'}
        Logger log level. Default: "INFO"
    """
    _valid_loglevels = ["INFO", "DEBUG", "WARNING", "ERROR"]

    if loglevel not in _valid_loglevels:
        raise ValueError(
            f"Provided log level {loglevel} is not permitted; must be in "
            f"{_valid_loglevels}."
        )
    logger.enable("peakdet")
    try:
        logger.remove(0)
    except ValueError:
        logger.warning(
            "The logger has been already enabled. If you want to"
            "change the log level of an existing logger, please"
            "refer to the change_loglevel() function. (Note: You can"
            "find the log_handle either from the initial call of this"
            "function, or the console logs)"
        )
        return
    log_handle = logger.add(
        sys.stderr, level=loglevel, backtrace=backtrace, diagnose=diagnose
    )
    logger.debug(f"Enabling logger with handle_id: {log_handle}")
    return log_handle


def change_loglevel(log_handle, loglevel, diagnose=True, backtrace=True):
    """
    Change the loguru logger's log level.

    The logger needs to be already enabled by `enable_logger()`.

    Parameters
    ----------
    log_handle : Enabled logger's handle, returned by `enable_logger()`
    loglevel : {'INFO', 'DEBUG', 'WARNING', 'ERROR'}
    """
    _valid_loglevels = ["INFO", "DEBUG", "WARNING", "ERROR"]

    if loglevel not in _valid_loglevels:
        raise ValueError(
            f"Provided log level {loglevel} is not permitted; must be in "
            f"{_valid_loglevels}."
        )
    logger.remove(log_handle)
    new_log_handle = logger.add(
        sys.stderr, level=loglevel, backtrace=backtrace, diagnose=diagnose
    )
    logger.info(
        f'Changing the logger log level to "{loglevel}" (New logger handle_id: '
        f"{new_log_handle})"
    )
    return new_log_handle


def disable_logger(log_handle=None):
    """
    Change the loguru logger's log level.

    The logger needs to be already enabled by `enable_logger()`.

    Parameters
    ----------
    log_handle : Enabled logger's handle, returned by `enable_logger()`
        Default: None
        If left as None, this function will disable all logger instances
    """
    if log_handle is None:
        logger.info("Disabling all logger instances")
        logger.remove()
    else:
        logger.info(f"Disabling logger with handle_id: {log_handle}")
        logger.remove(log_handle)
    logger.disable("peakdet")
