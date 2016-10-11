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
    
    @property
    def _peaksig(self):
        rravg = int(self.rrint.mean()*self.fs)
        peaksig = np.zeros((self.peakinds.shape[0],rravg))

        for n, p in enumerate(self.peakinds):
            sig = self.data[int(p-rravg)/2:int(p)]
            if sig.shape[0] < rravg: continue
            else: peaksig[n] = sig

        return peaksig
    
    def get_peaks(self, order=2, troughs=False):
        inds = comp_peaks(  self.data, 
                            self.filtsig, 
                            order=order, 
                            comparator=scipy.signal.argrelmax   )

        self._peakinds = np.unique(inds[self.filtsig[inds] > self.filtsig.mean()])
        self._peakinds.sort()

        if troughs: self.get_troughs(order=order)

    def get_troughs(self, order=2):
        if not hasattr(self,'peakinds'): self.get_peaks(order=order, troughs=False)

        inds = comp_peaks(  self.data, 
                            self.filtsig, 
                            order=order, 
                            comparator=scipy.signal.argrelmin,
                            k=3   )

        self._troughinds = np.unique(inds[self.filtsig[inds] < self.filtsig.mean()])
        self._check_troughs()

    def _check_troughs(self):
        for n in np.arange(1,self.peakinds.size):
            snip = np.logical_and(  self.troughinds >  self.peakinds[n-1],
                                    self.troughinds <= self.peakinds[n])
            troughs = self.troughinds[snip]

            if len(troughs) < 1:
                snippet = self.filtsig[self.peakinds[n-1]:self.peakinds[n]]
                troughs = np.where(snippet == snippet.min()) + self.peakinds[n-1]
                self._troughinds = np.append(self.troughinds, troughs[0])
            elif troughs.size > 1:
                trough_amp = self.filtsig[troughs]
                rej = troughs[np.where(trough_amp > trough_amp.min())[0]]
                for t in rej: 
                    self._troughinds = np.delete(self.troughinds,
                                                    np.where(self.troughinds == t)[0])

        self._troughinds.sort()

    def hard_thresh(self, sd=2.0, thresh=0.75):
        high = self._peaksig.mean(axis=0) + sd*self._peaksig.std(axis=0)
        low = self._peaksig.mean(axis=0) - sd*self._peaksig.std(axis=0)
        keep = np.ones(self._peaksig.shape[0], dtype='bool')

        for n, p in enumerate(self._peaksig):
            overlap = p[np.logical_and(p>low,p<high)].size
            if overlap < int(self._peaksig.shape[1]*thresh): keep[n] = 0
        
        self._peakinds = self.peakinds[keep]

    def classify(self):
        clf = DBSCAN(eps=1.0)
        classes = clf.fit_predict(self._peaksig)
        return classes

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