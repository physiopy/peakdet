# -*- coding: utf-8 -*-

import numpy as np
from sklearn.utils import Bunch


class Physio():
    """
    Helper class to hold physiological data and associated metadata

    Parameters
    ----------
    data : array_like
        Input data array
    fs : float, optional
        Sampling rate of `data` (Hz). Default: None
    history : list of tuples, optional
        Functions performed on `data`
    metadata : dict, optional
        Metadata associated with `data`
    """

    def __init__(self, data, fs=None, history=[], metadata=None):
        data = np.asarray(data).squeeze()
        if data.ndim > 1:
            raise ValueError('Provided data dimensionality {} > expected 1'
                             .format(data.ndim))
        self._data = data
        self._fs = np.float64(fs)
        self._history = history
        if metadata is not None:
            self._metadata = metadata
        else:
            self._metadata = Bunch(peaks=np.empty(0, dtype=int),
                                   troughs=np.empty(0, dtype=int),
                                   reject=np.empty(0, dtype=int))

    def __array__(self):
        return self.data

    def __getitem__(self, slicer):
        return self.data[slicer]

    def __str__(self):
        return '{name}(size={size}, fs={fs})'.format(
            name=self.__class__.__name__,
            size=self.data.size,
            fs=self.fs
        )

    __repr__ = __str__

    @property
    def data(self):
        """ Physiological data """
        return self._data

    @property
    def fs(self):
        """ Sampling rate of data (Hz) """
        return self._fs

    @property
    def history(self):
        """ Functions that have been performed on / modified `data` """
        return self._history

    @property
    def peaks(self):
        """ Indices of detected peaks in `data` """
        return self._masked.compressed()

    @property
    def troughs(self):
        """ Indices of detected troughs in `data` """
        return self._metadata.troughs

    @property
    def _masked(self):
        return np.ma.masked_array(self._metadata.peaks,
                                  mask=np.isin(self._metadata.peaks,
                                               self._metadata.reject))
