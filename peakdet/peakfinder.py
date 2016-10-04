#!/usr/bin/env python

import numpy as np
import scipy.signal
from sklearn.cluster import DBSCAN
from .physio import InterpolatedPhysio
from .utils import comp_peaks

class PeakFinder(InterpolatedPhysio):
    """Class with peak (and trough) finding method(s)"""

    def __init__(self, data, fs):
        super(PeakFinder,self).__init__(data, fs)
        self._peakinds = []
        self._troughinds = []

    @property
    def rrtime(self):
        if len(self.peakinds): 
            return self._peakinds[1:]/self.fs
        else: 
            return []

    @property
    def rrint(self):
        if len(self.peakinds): 
            return (self.peakinds[1:] - self.peakinds[:-1])/self.fs
        else: 
            return []

    @property
    def peakinds(self):
        return self._peakinds

    @property
    def troughinds(self):
        return self._troughinds

    def get_peaks(self, order=2, troughs=False):
        inds = comp_peaks(  self.data, 
                            self.filtsig, 
                            order=order, 
                            comparator=scipy.signal.argrelmax   )

        self._peakinds = inds[self.filtsig[inds] > self.filtsig.mean()]

        clf = DBSCAN()
        classes = clf.fit_predict(self._peaksig)

        if troughs: self.get_troughs()

    def get_troughs(self, order=2):
        if not hasattr(self,'peakinds'): self.get_peaks()

        inds = comp_peaks(  self.data, 
                            self.filtsig, 
                            order=order, 
                            comparator=scipy.signal.argrelmin   )

        self._troughinds = inds[self.filtsig[inds] < self.filtsig.mean()]
        
    @property
    def _peaksig(self):
        rravg = int(self.rrint.mean()*self.fs)
        peaksig = np.zeros((self.peakinds.shape[0],rravg))

        for n, p in enumerate(self.peakinds):
            sig = self.data[int(p-rravg/2):int(p+rravg/2)]
            if sig.shape[0] < rravg: continue
            else: peaksig[n] = sig

        return peaksig

    def hard_thresh(self, sd=2.0, thresh=0.90):
        high = self._peaksig.mean(axis=0) + sd*self._peaksig.std(axis=0)
        low = self._peaksig.mean(axis=0) - sd*self._peaksig.std(axis=0)
        keep = np.ones(self._peaksig.shape[0], dtype='bool')

        for n, p in enumerate(self._peaksig):
            overlap = p[np.logical_and(p>low,p<high)].size
            if overlap < int(self._peaksig.shape[1]*thresh): keep[n] = 0
        
        self._peakinds = self.peakinds[keep]

    def classify(self):
        clf = DBSCAN()
        classes = clf.fit_predict(self._peaksig)
        return classes

    def plot_data(self, filtsig=True, _test=False):
        import matplotlib.pyplot as plt
        t = np.arange(0,self.data.size/self.fs, 1./self.fs)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, self.data,'b')
        ax.plot(t[self.peakinds], self.data[self.peakinds],'.r')
        if filtsig:
            ax.plot(t,self.filtsig,'g')
            ax.plot(t[self.peakinds],self.filtsig[self.peakinds],'.c')
        if not _test: plt.show()
        else: plt.close()