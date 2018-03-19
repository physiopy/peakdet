# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import welch
from scipy.interpolate import interp1d


class HRV():
    """
    Class designed purely for housing calculation of various HRV statistics

    Parameters
    ----------
    rrtime : array-like
        Times at which RR-intervals occured (in sec)
    rrint : array-like
        RR-intervals (in msec)

    Notes
    -----
    Uses scipy.signal.welch for calculation of frequency-based statistics
    """

    def __init__(self, peakfinder):
        self.pf = peakfinder
        self._sd = np.diff(np.diff(self.pf._masked)).compressed()
        self._rrint = self.pf.rrint * 1000.

        func = interp1d(self.pf.rrtime, self._rrint, kind='cubic')
        irrt = np.arange(self.pf.rrtime[0], self.pf.rrtime[-1], 1. / 4.)
        self._irri = func(irrt)

    @property
    def _fft(self):
        return welch(self._irri, nperseg=120, fs=4.0, scaling='spectrum')

    @property
    def avgnn(self):
        return self._rrint.mean()

    @property
    def sdnn(self):
        return self._rrint.std()

    @property
    def rmssd(self):
        return np.sqrt((self._sd**2).mean())

    @property
    def sdsd(self):
        return self._sd.std()

    @property
    def nn50(self):
        return np.argwhere(self._sd > 50.).size

    @property
    def pnn50(self):
        return self.nn50 / self._rrint.size

    @property
    def nn20(self):
        return np.argwhere(self._sd > 20.).size

    @property
    def pnn20(self):
        return self.nn20 / self._rrint.size

    @property
    def _hf(self):
        fx, px = self._fft
        return px[np.logical_and(fx >= 0.15, fx < 0.40)]

    @property
    def _lf(self):
        fx, px = self._fft
        return px[np.logical_and(fx >= 0.04, fx < 0.15)]

    @property
    def _vlf(self):
        fx, px = self._fft
        return px[np.logical_and(fx >= 0., fx < 0.04)]

    @property
    def hf(self):
        return sum(self._hf)

    @property
    def hf_log(self):
        return np.log(self.hf)

    @property
    def lf(self):
        return sum(self._lf)

    @property
    def lf_log(self):
        return np.log(self.lf)

    @property
    def vlf(self):
        return sum(self._vlf)

    @property
    def vlf_log(self):
        return np.log(self.vlf)

    @property
    def lftohf(self):
        return self.lf / self.hf

    @property
    def hf_peak(self):
        fx, px = self._fft
        return fx[np.argmax(self._hf)]

    @property
    def lf_peak(self):
        fx, px = self._fft
        return fx[np.argmax(self._lf)]
