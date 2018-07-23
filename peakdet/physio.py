# -*- coding: utf-8 -*-

import numpy as np
from peakdet import editor, extrema


class Physio():
    """
    Helper class to hold physiological data and associated metadata

    Parameters
    ----------
    data : array_like
        Input data array
    fs : float, optional
        Sampling rate of ``data`` (Hz). Default: None
    """

    def __init__(self, data, fs=None):
        data = np.asarray(data).squeeze()
        if data.ndim > 1:
            raise ValueError('Provided data dimensionality {} > expected 1'
                             .format(data.ndim))
        self._fs = np.float64(fs)
        self._data = data
        self._metadata = dict(peaks=[], troughs=[],
                              reject=np.empty(0, dtype=int))

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


class PeakFinder(Physio):
    """
    Helper class for peak/trough finding in physio waveforms

    Parameters
    ----------
    data : array_like
        Input data array
    fs : float, optional
        Sampling rate of ``data`` (Hz). Default: None
    """

    def __init__(self, data, fs=None):
        super().__init__(data, fs)
        self._peaks, self._troughs = [], []
        self._reject = np.empty(0, dtype=int)

    @property
    def _masked(self):
        return np.ma.masked_array(self._peaks,
                                  mask=np.isin(self._peaks,
                                               self._reject))

    @property
    def rrtime(self):
        """ Times of R-R intervals (in seconds) """
        if len(self.peaks):
            diff = (self._masked[:-1] + self._masked[1:]) / (2 * self.fs)
            return diff.compressed()

    @property
    def rrint(self):
        """ Length of R-R intervals (in seconds) """
        if len(self.peaks):
            return (np.diff(self._masked) / self.fs).compressed()

    @property
    def peaks(self):
        """ Indices of detected peaks in data """
        return self._masked.compressed()

    @property
    def troughs(self):
        """ Indices of detected troughs in data """
        return self._troughs

    def find_peaks(self, thresh=0.2, dist=None):
        """
        Finds peaks in data

        Parameters
        ----------
        thresh : float [0,1], optional
            Relative height threshold data must surpass to be classified as a
            peak. Default: 0.2
        dist : int, optional
            Distance (in indices) that peaks must be separated by. If not
            specified, this is estimated from data.
        """

        if dist is None:
            dist = self.fs // 4

        locs = extrema.find_peaks(self.data,
                                  dist=dist,
                                  thresh=thresh)
        dist = np.diff(locs).mean() // 2
        self._peaks = extrema.find_peaks(self.data,
                                         dist=dist,
                                         thresh=thresh).astype(int)

        self._find_troughs(thresh=thresh, dist=dist)

    def _find_troughs(self, thresh=0.4, dist=None):
        """
        Detects troughs in data

        Parameters
        ----------
        thresh : float [0,1]
            determines relative height of data to be considered a trough
        """

        if dist is None:
            dist = self.fs // 4

        locs = extrema.find_troughs(self.data,
                                    dist=dist,
                                    thresh=thresh)
        troughs = extrema.find_troughs(self.data,
                                       dist=np.diff(locs).mean() // 2,
                                       thresh=thresh)
        self._troughs = extrema.check_troughs(self.data,
                                              self.peaks,
                                              troughs)

    def plot(self):
        raise NotImplementedError

    def edit(self):
        """
        Interactive peak editing tool
        """

        editor.PhysioEditor(self)
