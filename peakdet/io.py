# -*- coding: utf-8 -*-
"""
Functions for loading and saving data and analyses
"""

import json
import os.path as op
import warnings
import numpy as np
from peakdet import physio, utils
from loguru import logger

EXPECTED = ['data', 'fs', 'history', 'metadata']


@logger.catch
def load_physio(data, *, fs=None, dtype=None, history=None,
                allow_pickle=False):
    """
    Returns `Physio` object with provided data

    Parameters
    ----------
    data : str or array_like or Physio_like
        Input physiological data. If array_like, should be one-dimensional
    fs : float, optional
        Sampling rate of `data`. Default: None
    dtype : data_type, optional
        Data type to convert `data` to, if conversion needed. Default: None
    history : list of tuples, optional
        Functions that have been performed on `data`. Default: None
    allow_pickle : bool, optional
        Whether to allow loading if `data` contains pickled objects. Default:
        False

    Returns
    -------
    data: :class:`peakdet.Physio`
        Loaded physiological data

    Raises
    ------
    TypeError
        If provided `data` is unable to be loaded
    """

    # first check if the file was made with `save_physio`; otherwise, try to
    # load it as a plain text file and instantiate a history
    if isinstance(data, str):
        try:
            inp = dict(np.load(data, allow_pickle=allow_pickle))
            for attr in EXPECTED:
                try:
                    inp[attr] = inp[attr].dtype.type(inp[attr])
                except KeyError:
                    raise ValueError('Provided npz file {} must have all of '
                                     'the following attributes: {}'
                                     .format(data, EXPECTED))
            # fix history, which needs to be list-of-tuple
            if inp['history'] is not None:
                inp['history'] = list(map(tuple, inp['history']))
        except (IOError, OSError, ValueError):
            inp = dict(data=np.loadtxt(data),
                       history=[utils._get_call(exclude=[])])
        phys = physio.Physio(**inp)
    # if we got a numpy array, load that into a Physio object
    elif isinstance(data, np.ndarray):
        if history is None:
            logger.warning('Loading data from a numpy array without providing a'
                           'history will render reproducibility functions '
                           'useless! Continuing anyways.')
        phys = physio.Physio(np.asarray(data, dtype=dtype), fs=fs,
                             history=history)
    # create a new Physio object out of a provided Physio object
    elif isinstance(data, physio.Physio):
        phys = utils.new_physio_like(data, data.data, fs=fs, dtype=dtype)
        phys._history += [utils._get_call()]
    else:
        raise TypeError('Cannot load data of type {}'.format(type(data)))

    # reset sampling rate, as requested
    if fs is not None and fs != phys.fs:
        if not np.isnan(phys.fs):
            logger.warning('Provided sampling rate does not match loaded rate. '
                          'Resetting loaded sampling rate {} to provided {}'
                          .format(phys.fs, fs))
        phys._fs = fs
    # coerce datatype, if needed
    if dtype is not None:
        phys._data = np.asarray(phys[:], dtype=dtype)

    return phys


def save_physio(fname, data):
    """
    Saves `data` to `fname`

    Parameters
    ----------
    fname : str
        Path to output file; .phys will be appended if necessary
    data : Physio_like
        Data to be saved to file

    Returns
    -------
    fname : str
        Full filepath to saved output
    """

    from peakdet.utils import check_physio

    data = check_physio(data)
    fname += '.phys' if not fname.endswith('.phys') else ''
    with open(fname, 'wb') as dest:
        hist = data.history if data.history != [] else None
        np.savez_compressed(dest, data=data.data, fs=data.fs,
                            history=hist, metadata=data._metadata)

    return fname


@logger.catch
def load_history(file, verbose=False):
    """
    Loads history from `file` and replays it, creating new Physio instance

    Parameters
    ----------
    file : str
        Path to input JSON file
    verbose : bool, optional
        Whether to print messages as history is being replayed. Default: False

    Returns
    -------
    file : str
        Full filepath to saved output
    """

    # import inside function for safety!
    # we'll likely be replaying some functions from within this module...
    import peakdet

    # grab history from provided JSON file
    with open(file, 'r') as src:
        history = json.load(src)

    # replay history from beginning and return resultant Physio object
    data = None
    for (func, kwargs) in history:
        if verbose:
            logger.info('Rerunning {}'.format(func))
        # loading functions don't have `data` input because it should be the
        # first thing in `history` (when the data was originally loaded!).
        # for safety, check if `data` is None; someone could have potentially
        # called load_physio on a Physio object (which is a valid, albeit
        # confusing, thing to do)
        if 'load' in func and data is None:
            if not op.exists(kwargs['data']):
                if kwargs['data'].startswith('/'):
                    msg = ('Perhaps you are trying to load a history file '
                           'that was generated with an absolute path?')
                else:
                    msg = ('Perhaps you are trying to load a history file '
                           'that was generated from a different directory?')
                raise FileNotFoundError('{} does not exist. {}'
                                        .format(kwargs['data'], msg))
            data = getattr(peakdet, func)(**kwargs)
        else:
            data = getattr(peakdet, func)(data, **kwargs)

    return data


def save_history(file, data):
    """
    Saves history of physiological `data` to `file`

    Saved file can be replayed with `peakdet.load_history`

    Parameters
    ----------
    file : str
        Path to output file; .json will be appended if necessary
    data : Physio_like
        Data with history to be saved to file

    Returns
    -------
    file : str
        Full filepath to saved output
    """

    from peakdet.utils import check_physio

    data = check_physio(data)
    if len(data.history) == 0:
        logger.warning('History of provided Physio object is empty. Saving '
                       'anyway, but reloading this file will result in an '
                       'error.')
    file += '.json' if not file.endswith('.json') else ''
    with open(file, 'w') as dest:
        json.dump(data.history, dest, indent=4)

    return file
