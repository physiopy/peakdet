"""
Functions and classes for generating analytics on physiological data
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import welch


class HRV:
    """
    Class for calculating various HRV statistics

    Parameters
    ----------
    data : Physio_like
        Physiological data object with detected peaks and troughs

    Attributes
    ----------
    rrint : :obj:`numpy.ndarray`
        R-R intervals derived from `data` (sometimes referred to as N-N
        intervals in derived metrics)
    rrtime : :obj:`numpy.ndarray`
        Time stamps of `rrint`
    avgnn : float
        Average heart rate (N-N interval)
    sdnn : float
        Standard deviation of heart rate (N-N intervals)
    rmssd : float
        Root mean square of successive differences
    sdsd : float
        Standard deviation of successive differences
    nn50 : float
        Number of N-N intervals greater than 50ms
    pnn50 : float
        Percent of N-N intervals greater than 50ms
    nn20 : float
        Number of N-N intervals greater than 20ms
    pnn20 : float
        Percent of N-N intervals greater than 20ms
    hf : float
        High-frequency power of R-R intervals, summed across 0.15-0.40 Hz
    hf_log : float
        Log of `hf`
    lf : float
        Low-frequency power of R-R intervals, summed across 0.04-0.15 Hz
    lf_log : float
        Log of `lf`
    vlf : float
        Very low frequency power of R-R intervals, summed across 0-0.04 Hz
    vlf_log : float
        Log of `vlf`
    lftohf : float
        Ratio of `lf` over `hf`
    hf_peak : float
        Peak frequency in `hf` band (0.15-0.40 Hz)
    lf_peak : float
        Peak frequency in `lf` band (0.04-0.15 Hz)

    Notes
    -----
    Uses scipy.signal.welch for calculation of frequency-based statistics
    """

    def __init__(self, data):
        self.data = data
        func = interp1d(self.rrtime, self.rrint * 1000, kind="cubic")
        irrt = np.arange(self.rrtime[0], self.rrtime[-1], 1.0 / 4.0)
        self._irri = func(irrt)

    @property
    def rrtime(self):
        """Times of R-R intervals (in seconds)"""
        if len(self.data.peaks):
            diff = (self.data._masked[:-1] + self.data._masked[1:]) / (2 * self.data.fs)
            return diff.compressed()

    @property
    def rrint(self):
        """Length of R-R intervals (in seconds)"""
        if len(self.data.peaks):
            return (np.diff(self.data._masked) / self.data.fs).compressed()

    @property
    def _sd(self):
        return np.diff(np.diff(self.data._masked)).compressed()

    @property
    def _fft(self):
        return welch(self._irri, nperseg=120, fs=4.0, scaling="spectrum")

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
        return np.argwhere(self._sd > 50.0).size

    @property
    def pnn50(self):
        return self.nn50 / self.rrint.size

    @property
    def nn20(self):
        return np.argwhere(self._sd > 20.0).size

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
        return px[np.logical_and(fx >= 0.0, fx < 0.04)]

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
