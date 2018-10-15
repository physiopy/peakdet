# -*- coding: utf-8 -*-
"""
Functions and classes for generating analytics on physiological data
"""

import numpy as np
from scipy.signal import welch
from scipy.interpolate import interp1d


class HRV():
    """
    Class for calculating various HRV statistics

    Parameters
    ----------
    data : Physio_like
        Physiological data object with detected peaks and troughs

    Attributes
    ----------
    rrtime : :obj:`numpy.ndarray`
    rrint : :obj:`numpy.ndarray`
    avgnn : float
    sdnn : float
    rmssd : float
    sdsd : float
    nn50 : float
    pnn50 : float
    nn20 : float
    pnn20 : float
    hf : float
    hf_log : float
    lf : float
    lf_log : float
    vlf : float
    vlf_log : float
    lftohf : float
    hf_peak : float
    lf_peak : float

    Notes
    -----
    Uses scipy.signal.welch for calculation of frequency-based statistics
    """

    def __init__(self, data):
        self.data = data
        func = interp1d(self.rrtime, self.rrint * 1000, kind='cubic')
        irrt = np.arange(self.rrtime[0], self.rrtime[-1], 1. / 4.)
        self._irri = func(irrt)

    @property
    def rrtime(self):
        """ Times of R-R intervals (in seconds) """
        if len(self.data.peaks):
            diff = ((self.data._masked[:-1] + self.data._masked[1:]) /
                    (2 * self.data.fs))
            return diff.compressed()

    @property
    def rrint(self):
        """ Length of R-R intervals (in seconds) """
        if len(self.data.peaks):
            return (np.diff(self.data._masked) / self.data.fs).compressed()

    @property
    def _sd(self):
        return np.diff(np.diff(self.data._masked)).compressed()

    @property
    def _fft(self):
        return welch(self._irri, nperseg=120, fs=4.0, scaling='spectrum')

    @property
    def avgnn(self):
        return self.rrint.mean() * 1000

    @property
    def sdnn(self):
        return self.rrint.std() * 1000

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
        return self.nn50 / self.rrint.size

    @property
    def nn20(self):
        return np.argwhere(self._sd > 20.).size

    @property
    def pnn20(self):
        return self.nn20 / self.rrint.size

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
