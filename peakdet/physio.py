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
        Functions performed on `data`. Default: None
    metadata : dict, optional
        Metadata associated with `data`. Default: None
    """

    def __init__(self, data, fs=None, history=None, metadata=None):
        self._data = np.asarray(data).squeeze()
        if self.data.ndim > 1:
            raise ValueError('Provided data dimensionality {} > 1.'
                             .format(self.data.ndim))
        if not np.issubdtype(self.data.dtype, np.number):
            raise ValueError('Provided data of type {} is not numeric.'
                             .format(self.data.dtype))
        self._fs = np.float64(fs)
        self._history = [] if history is None else history
        if (not isinstance(self._history, list) or
                any([not isinstance(f, tuple) for f in self._history])):
            raise TypeError('Provided history {} must be a list-of-tuples. '
                            'Please check inputs.'.format(history))
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError('Provided metadata {} must be dict-like.'
                                .format(metadata))
            for k in ['peaks', 'troughs', 'reject']:
                metadata.setdefault(k, np.empty(0, dtype=int))
                if not isinstance(metadata.get(k), np.ndarray):
                    try:
                        metadata[k] = np.asarray(metadata.get(k), dtype=int)
                    except TypeError:
                        raise TypeError('Provided metadata must be dict-like'
                                        'with integer array entries.')
            self._metadata = Bunch(**metadata)
        else:
            self._metadata = Bunch(peaks=np.empty(0, dtype=int),
                                   troughs=np.empty(0, dtype=int),
                                   reject=np.empty(0, dtype=int))

    def __array__(self):
        return self.data

    def __getitem__(self, slicer):
        return self.data[slicer]

    def __len__(self):
        return len(self.data)

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
