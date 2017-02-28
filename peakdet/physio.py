#!/usr/bin/env python

from __future__ import absolute_import
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from peakdet import utils


class Physio(object):
    """
    Class to handle an instance of physiological data
    """

    def __init__(self, data, fs):
        self._fs = float(fs)
        self._dinput = data

    @property
    def fs(self):
        return self._fs

    @fs.setter
    def fs(self, value):
        self._fs = float(value)

    @property
    def rawdata(self):
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
    """

    def __init__(self, data, fs):
        super(ScaledPhysio,self).__init__(data,fs)
        self._data = utils.normalize(self.rawdata)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = np.asarray(value)


class FilteredPhysio(ScaledPhysio):
    """Class with filtering method"""

    def __init__(self, data, fs):
        super(FilteredPhysio,self).__init__(data,fs)
        self._filtsig = self.data.copy()

    @property
    def flims(self):
        return utils.gen_flims(self.filtsig, self.fs)

    @property
    def filtsig(self):
        if not np.all(self._filtsig==self.data): return self._filtsig
        else: return self.data

    def reset(self):
        """
        Resets self.filtsig to original (scaled) data series
        """
        self._filtsig = self.data.copy()

    def bandpass(self, flims=None):
        """
        Bandpass filters signal with frequency cutoffs `flims`
        """
        if flims is None: flims = self.flims
        self._filtsig = utils.bandpass_filt(self._filtsig,
                                            self.fs,
                                            flims)

    def lowpass(self, flims=None):
        """
        Lowpass filters signal with frequency cutoff `flims`
        """
        if flims is None: flims = self.flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[0]
        self._filtsig = utils.bandpass_filt(self._filtsig,
                                            self.fs,
                                            flims,
                                            btype='low')

    def highpass(self, flims=None):
        """
        Highpass filters signal with frequency cutoff `flims`
        """
        if flims is None: flims = self.flims
        if hasattr(flims,'__len__') and len(flims) > 1: flims = flims[-1]
        self._filtsig = utils.bandpass_filt(self._filtsig,
                                            self.fs,
                                            flims,
                                            btype='high')


class InterpolatedPhysio(FilteredPhysio):
    """
    Class with interpolation method
    """

    def __init__(self, data, fs):
        super(InterpolatedPhysio,self).__init__(data,fs)
        self._rawfs = fs

    def interpolate(self, order=2):
        """
        Interpolates self.data to sampling rate `order` * self.fs
        """
        t = np.arange(0, self.data.size/self.fs, 1./self.fs)
        if t.size != self.data.size: t = t[:self.data.size]

        tn = np.arange(0, t[-1], 1./(self.fs*order))
        i = InterpolatedUnivariateSpline(t,self.data)

        self.data, self.fs = i(tn), self.fs*order
        self.reset()

    def reset(self, hard=False):
        if hard:
            super(InterpolatedPhysio,self).__init__(self._dinput,self._rawfs)
        else:
            super(InterpolatedPhysio,self).reset()


class PeakFinder(InterpolatedPhysio):
    """
    Class with peak (and trough) finding method(s)
    """

    def __init__(self, data, fs):
        super(PeakFinder,self).__init__(data, fs)
        self._peakinds, self._troughinds = [], []

    @property
    def rrtime(self):
        if len(self.peakinds): return self._peakinds[1:]/self.fs
        else: return

    @property
    def rrint(self):
        if len(self.peakinds): return np.diff(self.peakinds)/self.fs
        else: return

    @property
    def peakinds(self):
        return self._peakinds

    @property
    def troughinds(self):
        return self._troughinds

    @property
    def _peaksig(self):
        if self.rrtime is None: return
        else: return utils.gen_temp(self.filtsig,self.peakinds)

    @property
    def template(self):
        if self.rrtime is None: return
        else: return utils.corr_template(self._peaksig)

    def get_peaks(self, thresh=0.4):
        locs = utils.peakfinder(self.filtsig,
                                dist=int(self.fs/4),
                                thresh=thresh)
        self._peakinds = utils.peakfinder(self.filtsig,
                                          dist=round(np.diff(locs).mean())/2,
                                          thresh=thresh)
        self._peakinds = utils.match_temp(self.filtsig,
                                          self._peakinds,
                                          self.template)

        self.get_troughs()

    def get_troughs(self, thresh=0.4):
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

    def plot_data(self, _test=False):
        import matplotlib.pyplot as plt
        t = np.arange(0,self.filtsig.size/self.fs, 1./self.fs)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, self.filtsig,'b')
        if hasattr(self, 'peakinds'):
            ax.plot(t[self.peakinds], self.filtsig[self.peakinds],'.r')
        if hasattr(self, 'troughinds'):
            ax.plot(t[self.troughinds], self.filtsig[self.troughinds],'.g')
        if not _test: plt.show()
        else: plt.close()
