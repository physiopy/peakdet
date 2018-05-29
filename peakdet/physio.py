# -*- coding: utf-8 -*-

from __future__ import absolute_import
import numpy as np
from peakdet import utils, editor


class Physio(object):
    """
    Class to hold physiological data

    Parameters
    ----------
    data : str or array_like
        Input data filename or array
    fs : float
        Sampling rate (Hz) of ``data``
    """

    def __init__(self, data, fs):
        self._fs = self._rawfs = float(fs)
        self._input = data
        self.rawdata = data.copy()
        self._data = utils.normalize(self.rawdata)
        self._filtsig = self._data.copy()

    @property
    def fs(self):
        """ Sampling rate (Hz) """
        return self._fs

    @property
    def time(self):
        """ Array of time points corresponding to data """
        return np.arange(0, self.data.size / self.fs, 1. / self.fs)

    @property
    def _flims(self):
        """ Approximate frequency cutoffs for peak detection """
        return utils.gen_flims(self.data, self.fs)

    @property
    def data(self):
        """ Filtered data """
        return self._data

    def reset(self, hard=False):
        """
        Removes filtering from data

        Parameters
        ----------
        hard : bool (False)
            also remove interpolation from data
        """

        if hard:
            self.__init__(self._input, self._rawfs)
        else:
            self.data = self._data.copy()


class PeakFinder(Physio):
    """
    Class with peak (and trough) finding method(s)

    Parameters
    ----------
    data : str or array_like
        Input data filename or array
    fs : float
        Sampling rate (Hz) of ``data``
    col : int, optional
        Column of data in input file, if ``data`` is str. Default: 0
    header : bool, optional
        Whether ``data`` has a header, if ``data`` is str. Default: False
    """

    def __init__(self, data, fs, col=0, header=False):
        super().__init__(data, fs, col, header)
        self._peakinds, self._troughinds = [], []
        self._rejected = np.empty(0, dtype='int')

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
        else:
            return

    @property
    def rrint(self):
        """ Length of R-R intervals (in seconds) """
        if len(self.peakinds):
            return (np.diff(self._masked) / self.fs).compressed()
        else:
            return

    @property
    def peakinds(self):
        """ Indices of detected peaks in data """
        return self._masked.compressed()

    @property
    def troughinds(self):
        """ Indices of detected troughs in data """
        return self._troughinds

    @property
    def _peaksig(self):
        if self.rrtime is None:
            return
        else:
            return utils.gen_temp(self.data, self.peakinds)

    @property
    def _template(self):
        if self.rrtime is None:
            return
        else:
            return utils.corr_template(self._peaksig)

    def reset(self, hard=False):
        """
        Removes filtering and peak-finding from data

        Parameters
        ----------
        hard : bool (False)
            also remove interpolation from data
        """

        self._peakinds, self._troughinds = [], []
        super(PeakFinder, self).reset(hard=hard)

    def get_peaks(self, thresh=0.2, dist=None):
        """
        Detects peaks in data

        Parameters
        ----------
        thresh : float [0,1]
            determines relative height of data to be considered a peak
        """

        if dist is None:
            dist = int(self.fs / 4)
        locs = utils.peakfinder(self.data,
                                dist=dist,
                                thresh=thresh)
        self._peakinds = utils.peakfinder(self.data,
                                          dist=round(np.diff(locs).mean()) / 2,
                                          thresh=thresh).astype('int')

        self.get_troughs(thresh=thresh, dist=dist)

    def get_troughs(self, thresh=0.4, dist=None):
        """
        Detects troughs in data

        Parameters
        ----------
        thresh : float [0,1]
            determines relative height of data to be considered a trough
        """

        if dist is None:
            dist = int(self.fs / 4)
        if self.rrtime is None:
            self.get_peaks(thresh=thresh, dist=dist)

        locs = utils.troughfinder(self.data,
                                  dist=dist,
                                  thresh=thresh)
        troughinds = utils.troughfinder(self.data,
                                        dist=round(np.diff(locs).mean()) / 2,
                                        thresh=thresh)
        self._troughinds = utils.check_troughs(self.data,
                                               troughinds,
                                               self.peakinds)

    def plot(self, _debug=False):
        """ Generates plot of data with detected peaks/troughs (if any) """

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1)
        ax.plot(self.time, self.data, 'b')

        if len(self.peakinds):
            ax.plot(self.time[self.peakinds],
                    self.data[self.peakinds], '.r')
        if len(self.troughinds):
            ax.plot(self.time[self.troughinds],
                    self.data[self.troughinds], '.g')

        if not _debug:
            plt.show()

        return fig

    def edit_peaks(self, _xlim=None):
        """
        Opens up peakdet.editor.PeakEditor window

        This is for interactive editing of detected peaks (i.e., is to be used
        to remove components of the data stream contaminated by artifact). To
        use, simply drag the cursor over parts of the data to remove them from
        consideration.

        Accepted inputs
        ---------------
        <ctrl-z> : undo last edit
        <ctrl-q> : stop interactive peak editing
        """

        editor.PeakEditor(self, _xlim=_xlim)
