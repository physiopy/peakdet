# -*- coding: utf-8 -*-

from __future__ import absolute_import
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from peakdet import utils, editor


class Physio(object):
    """
    Class to hold physiological data

    Parameters
    ----------
    data : str, array, list
        input data
    fs : float
        sampling rate (Hz)
    """

    def __init__(self, data, fs):
        self._fs = float(fs)
        self._dinput = data

    @property
    def fs(self):
        """
        Sampling rate (Hz)
        """

        return self._fs

    @fs.setter
    def fs(self, value):
        self._fs = float(value)

    @property
    def rawdata(self):
        """
        Original (input) data
        """
        if isinstance(self._dinput, (str)):
            try:
                return np.loadtxt(self._dinput)
            except ValueError:
                return np.loadtxt(self._dinput, skiprows=1)
        elif isinstance(self._dinput, (np.ndarray, list)):
            return np.asarray(self._dinput)
        else:
            raise TypeError("Data input must be filename or array-like.")


class ScaledPhysio(Physio):
    """
    Class that normalizes input data

    Parameters
    ----------
    data : str, array, list
        input data
    fs : float
        sampling rate (Hz)
    """

    def __init__(self, data, fs):
        super(ScaledPhysio, self).__init__(data, fs)
        self._data = utils.normalize(self.rawdata)

    @property
    def data(self):
        """
        Normalized (centered + standardized) data
        """

        return self._data

    @data.setter
    def data(self, value):
        self._data = np.asarray(value)

    @property
    def time(self):
        """
        Array of time points corresponding to data
        """

        return np.arange(0, self.data.size / self.fs, 1. / self.fs)


class FilteredPhysio(ScaledPhysio):
    """
    Class with ability to filter data

    Parameters
    ----------
    data : str, array, list
        input data
    fs : float
        sampling rate (Hz)
    """

    def __init__(self, data, fs):
        super(FilteredPhysio, self).__init__(data, fs)
        self._filtsig = self._data.copy()

    @property
    def _flims(self):
        """
        Approximated frequency cutoffs for peak detection
        """

        return utils.gen_flims(self.data, self.fs)

    @property
    def data(self):
        """
        Filtered data
        """

        return self._filtsig

    @data.setter
    def data(self, value):
        self._filtsig = np.asarray(value)

    def reset(self):
        """
        Resets data prior to filtering
        """

        self.data = self._data.copy()

    def bandpass(self, flims=None):
        """
        Bandpass filters signal

        Parameters
        ----------
        flims : list
            frequency cutoffs for filter (retain flims[0] < freq < flims[1])
        """

        if flims is None:
            flims = self._flims
        self.data = utils.bandpass_filt(self.data, self.fs,
                                        flims)

    def lowpass(self, flims=None):
        """
        Lowpass filters signal

        Parameters
        ----------
        flims : float
            frequency cutoff for filter (retain freq < flims)
        """

        if flims is None:
            flims = self._flims
        if hasattr(flims, '__len__') and len(flims) > 1:
            flims = flims[0]
        self.data = utils.bandpass_filt(self.data, self.fs,
                                        flims, btype='low')

    def highpass(self, flims=None):
        """
        Highpass filters signal

        Parameters
        ----------
        flims : float
            frequency cutoff for filter (retain freq > flims)
        """

        if flims is None:
            flims = self._flims
        if hasattr(flims, '__len__') and len(flims) > 1:
            flims = flims[-1]
        self.data = utils.bandpass_filt(self.data, self.fs,
                                        flims, btype='high')


class InterpolatedPhysio(FilteredPhysio):
    """
    Class with ability to interpolate input data

    Parameters
    ----------
    data : str, array, list
        input data
    fs : float
        sampling rate (Hz)
    """

    def __init__(self, data, fs):
        super(InterpolatedPhysio, self).__init__(data, fs)
        self._rawfs = fs

    def interpolate(self, order=2):
        """
        Interpolates data, to help improve peak-finding abilities

        Parameters
        ----------
        order : float (default: 2)
            data will be interpolated to order * fs
        """

        t = np.arange(0, self.data.size / self.fs, 1. / self.fs)
        if t.size != self.data.size:
            t = t[:self.data.size]

        tn = np.arange(0, t[-1], 1. / (self.fs * order))
        i = InterpolatedUnivariateSpline(t, self.data)

        self._data, self.fs = i(tn), self.fs*order
        self.reset()

    def reset(self, hard=False):
        """
        Removes filtering from data

        Parameters
        ----------
        hard : bool (False)
            also remove interpolation from data
        """

        if hard:
            super(InterpolatedPhysio, self).__init__(self._dinput, self._rawfs)
        else:
            super(InterpolatedPhysio, self).reset()


class PeakFinder(InterpolatedPhysio):
    """
    Class with peak (and trough) finding method(s)

    Parameters
    ----------
    data : str, array, list
        input data
    fs : float
        sampling rate (Hz)
    """

    def __init__(self, data, fs):
        super(PeakFinder, self).__init__(data, fs)
        self._peakinds, self._troughinds = [], []
        self._rejected = np.empty(0, dtype='int')

    @property
    def _irej(self):
        inds = [np.where(self._peakinds == r)[0][0] for r in self._rejected]
        inds = np.unique(np.append(inds, np.array(inds)-1))
        return inds[np.where(inds >= 0)].astype('int')

    @property
    def rrtime(self):
        """
        Times of R-R intervals (in seconds)
        """

        if len(self.peakinds):
            return np.delete(self._peakinds, self._irej)[1:]/self.fs
        else:
            return

    @property
    def rrint(self):
        """
        Length of R-R intervals (in seconds)
        """

        if len(self.peakinds):
            return np.delete(np.diff(self._peakinds), self._irej)/self.fs
        else:
            return

    @property
    def peakinds(self):
        """
        Indices of detected peaks in data
        """

        return np.setdiff1d(self._peakinds, self._rejected)

    @property
    def troughinds(self):
        """
        Indices of detected troughs in data
        """

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

    def get_peaks(self, thresh=0.4, dist=None):
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
                                          dist=round(np.diff(locs).mean())/2,
                                          thresh=thresh).astype('int')
        # self._peakinds = utils.match_temp(self.data,
        #                                   self.peakinds,
        #                                   self._template)

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
                                        dist=round(np.diff(locs).mean())/2,
                                        thresh=thresh)
        self._troughinds = utils.check_troughs(self.data,
                                               troughinds,
                                               self.peakinds)

    def plot(self, _debug=False):
        """
        Generates plot of data with detected peaks/troughs (if any)
        """

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
