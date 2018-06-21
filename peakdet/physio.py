# -*- coding: utf-8 -*-

import numpy as np
from peakdet import utils


class Physio():
    """
    Small class to hold physiological data

    Parameters
    ----------
    data : array_like
        Input data array
    fs : float
        Sampling rate of ``data`` (Hz)
    """

    def __init__(self, data, fs=None):
        data = np.asarray(data).squeeze()
        if data.ndim > 1:
            raise ValueError('Provided data dimensionality {} > expected 1'
                             .format(data.ndim))
        self._fs = np.float64(fs)
        self._data = data

    def __array__(self):
        return self.data

    def __getitem__(self, slicer):
        return self.data[slicer]

    def __str__(self):
        return '{name}(size={size}, fs={fs})'.format(
            name=self.__class__.__name__,
            size=self.size,
            fs=self.fs
        )

    __repr__ = __str__

    @property
    def size(self):
        return self.data.size

    @property
    def data(self):
        """ Physiological data """
        return self._data

    @property
    def fs(self):
        """ Sampling rate of data (Hz) """
        return self._fs

    def plot(self):
        raise NotImplementedError


class PeakFinder(Physio):
    """
    Class with peak (and trough) finding method(s)

    Parameters
    ----------
    data : str or array_like
        Input data filename or array
    fs : float
        Sampling rate (Hz) of ``data``
    """

    def __init__(self, data, fs=None):
        super().__init__(data, fs)
        self._peakinds, self._troughinds = [], []
        self._rejected = np.empty(0, dtype=int)

    @property
    def _masked(self):
        return np.ma.masked_array(self._peakinds,
                                  mask=np.isin(self._peakinds,
                                               self._rejected))

    @property
    def rrtime(self):
        """ Times of R-R intervals (in seconds) """
        if len(self.peakinds):
            diff = (self._masked[:-1] + self._masked[1:]) / (2 * self.fs)
            return diff.compressed()

    @property
    def rrint(self):
        """ Length of R-R intervals (in seconds) """
        if len(self.peakinds):
            return (np.diff(self._masked) / self.fs).compressed()

    @property
    def peakinds(self):
        """ Indices of detected peaks in data """
        return self._masked.compressed()

    @property
    def troughinds(self):
        """ Indices of detected troughs in data """
        return self._troughinds

    def get_peaks(self, thresh=0.2, dist=None):
        """
        Detects peaks in data

        Parameters
        ----------
        thresh : float [0,1], optional
            Determines relative height of data to be considered a peak.
            Default: 0.2
        dist : int, optional
        """

        locs = utils.find_peaks(self.data,
                                dist=self.fs // 4 if dist is None else dist,
                                thresh=thresh)
        self._peakinds = utils.find_peaks(self.data,
                                          dist=np.diff(locs).mean() // 2,
                                          thresh=thresh).astype(int)

        self.get_troughs(thresh=thresh, dist=dist)

    def get_troughs(self, thresh=0.4, dist=None):
        """
        Detects troughs in data

        Parameters
        ----------
        thresh : float [0,1]
            determines relative height of data to be considered a trough
        """

        if self.rrtime is None:
            self.get_peaks(thresh=thresh, dist=dist)

        locs = utils.find_troughs(self.data,
                                  dist=self.fs // 4 if dist is None else dist,
                                  thresh=thresh)
        troughinds = utils.find_troughs(self.data,
                                        dist=np.diff(locs).mean() // 2,
                                        thresh=thresh)
        self._troughinds = utils.check_troughs(self.data,
                                               self.peakinds,
                                               troughinds)
