#!/usr/bin/env python

import numpy as np
from .physio import InterpolatedPhysio
from . import utils


class PeakFinder(InterpolatedPhysio):
    """Class with peak (and trough) finding method(s)"""

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
        return utils.gen_temp(self.data,self.peakinds)

    def get_peaks(self):
        locs = utils.peakfinder(self.data,dist=int(self.fs/4))
        avgrate = round(np.diff(locs).mean())

        self._peakinds = utils.peakfinder(self.data,dist=avgrate/2)

        self.get_troughs()

    def get_troughs(self):
        if not hasattr(self,'peakinds'): self.get_peaks()

        locs = utils.troughfinder(self.data,dist=int(self.fs/4))
        avgrate = round(np.diff(locs).mean())

        troughinds = utils.troughfinder(self.data,dist=avgrate/2,)
        self._troughinds = utils.check_troughs(self.data,
                                               troughinds,
                                               self.peakinds)

    def plot_data(self, _test=False):
        import matplotlib.pyplot as plt
        t = np.arange(0,self.data.size/self.fs, 1./self.fs)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, self.data,'b')
        if hasattr(self, 'peakinds'):
            ax.plot(t[self.peakinds], self.data[self.peakinds],'.r')
        if hasattr(self, 'troughinds'):
            ax.plot(t[self.troughinds], self.data[self.troughinds],'.g')
        if not _test: plt.show()
        else: plt.close()
