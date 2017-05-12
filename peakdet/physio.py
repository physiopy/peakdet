#!/usr/bin/env python

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
            try: return np.loadtxt(self._dinput)
            except ValueError: return np.loadtxt(self._dinput,skiprows=1)
        elif isinstance(self._dinput, (np.ndarray,list)):
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
        super(ScaledPhysio,self).__init__(data,fs)
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
        super(FilteredPhysio,self).__init__(data,fs)
        self._filtsig = self.data.copy()

    @property
    def _flims(self):
        return utils.gen_flims(self.filtsig, self.fs)

    @property
    def filtsig(self):
        """
        Filtered data
        """

        if not np.all(self._filtsig==self.data): return self._filtsig
        else: return self.data

    def reset(self):
        """
        Resets data prior to filtering
        """

        self._filtsig = self.data.copy()

    def bandpass(self, flims=None):
        """
        Bandpass filters signal

        Parameters
        ----------
        flims : list
            frequency cutoffs for filter (retain flim[0] < freq < flim[1])
        """

        if flims is None: flims = self._flims
        self._filtsig = utils.bandpass_filt(self._filtsig,
                                            self.fs,
                                            flims)

    def lowpass(self, flims=None):
        """
        Lowpass filters signal

        Parameters
        ----------
        flims : float
            frequency cutoff for filter (retain freq < flim)
        """

        if flims is None: flims = self._flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[0]
        self._filtsig = utils.bandpass_filt(self._filtsig,
                                            self.fs,
                                            flims,
                                            btype='low')

    def highpass(self, flims=None):
        """
        Highpass filters signal

        Parameters
        ----------
        flims : float
            frequency cutoff for filter (retain freq > flim)
        """

        if flims is None: flims = self._flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[-1]
        self._filtsig = utils.bandpass_filt(self._filtsig,
                                            self.fs,
                                            flims,
                                            btype='high')


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
        super(InterpolatedPhysio,self).__init__(data,fs)
        self._rawfs = fs

    def interpolate(self, order=2):
        """
        Interpolates data, to help improve peak-finding abilities

        Parameters
        ----------
        order : float (2)
            data will be interpolated to order * fs
        """

        t = np.arange(0, self.filtsig.size/self.fs, 1./self.fs)
        if t.size != self.filtsig.size: t = t[:self.filtsig.size]

        tn = np.arange(0, t[-1], 1./(self.fs*order))
        i = InterpolatedUnivariateSpline(t,self.filtsig)

        self.data, self.fs = i(tn), self.fs*order
        self.reset()

    def reset(self, hard=False):
        """
        Resets data

        Parameters
        ----------
        hard : bool (False)
            causes data reset to remove interpolation
        """

        if hard:
            super(InterpolatedPhysio,self).__init__(self._dinput,self._rawfs)
        else:
            super(InterpolatedPhysio,self).reset()


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
        super(PeakFinder,self).__init__(data, fs)
        self._peakinds, self._troughinds = [], []

    @property
    def rrtime(self):
        """
        Times of R-R intervals (in seconds)
        """

        if len(self.peakinds): return self._peakinds[1:]/self.fs
        else: return

    @property
    def rrint(self):
        """
        R-R intervals of detected peaks (in seconds)
        """

        if len(self.peakinds): return np.diff(self.peakinds)/self.fs
        else: return

    @property
    def peakinds(self):
        """
        Indices of detected peaks in data
        """

        return self._peakinds

    @property
    def troughinds(self):
        """
        Indices of detected troughs in data
        """

        return self._troughinds

    @property
    def _peaksig(self):
        if self.rrtime is None: return
        else: return utils.gen_temp(self.filtsig,self.peakinds)

    @property
    def _template(self):
        if self.rrtime is None: return
        else: return utils.corr_template(self._peaksig)

    @property
    def time(self):
        """
        Array of time points corresponding to data
        """

        return np.arange(0,self.filtsig.size/self.fs, 1./self.fs)

    def get_peaks(self, thresh=0.4):
        """
        Detects peaks in data

        Parameters
        ----------
        thresh : float [0,1]
            determines relative height of data to be considered a peak
        """

        locs = utils.peakfinder(self.filtsig,
                                dist=int(self.fs/4),
                                thresh=thresh)
        self._peakinds = utils.peakfinder(self.filtsig,
                                          dist=round(np.diff(locs).mean())/2,
                                          thresh=thresh).astype('int64')
        # self._peakinds = utils.match_temp(self.filtsig,
        #                                   self._peakinds,
        #                                   self._template)

        self.get_troughs()

    def get_troughs(self, thresh=0.4):
        """
        Detects troughs in data

        Parameters
        ----------
        thresh : float [0,1]
            determines relative height of data to be considered a trough
        """

        if self.rrtime is None: self.get_peaks(thresh=thresh)

        locs = utils.troughfinder(self.filtsig,
                                  dist=int(self.fs/4),
                                  thresh=thresh)
        troughinds = utils.troughfinder(self.filtsig,
                                        dist=round(np.diff(locs).mean())/2,
                                        thresh=thresh)
        self._troughinds = utils.check_troughs(self.filtsig,
                                               troughinds,
                                               self.peakinds)

    def plot_data(self):
        """
        Generates plot of data with detected peaks/troughs (if any)
        """

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1)

        ax.plot(self.time, self.filtsig,'b')

        if len(self.peakinds)>0:
            ax.plot(self.time[self.peakinds],
                    self.filtsig[self.peakinds],'.r')
        if len(self.troughinds)>0:
            ax.plot(self.time[self.troughinds],
                    self.filtsig[self.troughinds],'.g')

        plt.show()

    def edit_peaks(self):
        """
        Opens up peakdet.editor.PeakEditor window

        This is for interactive editing of detected peaks (i.e., is to be used
        to remove components of the data stream contaminated by artifact). To
        use, simply drag the cursor over parts of the data to remove them from
        consideration.

        Accepted keys
        -------------
        <ctrl-z> : undo last removal
        <ctrl-q> : stop interactive peak editing
        """

        editor.PeakEditor(self)
