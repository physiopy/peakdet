#!/usr/bin/env python

import numpy as np
import scipy.signal
from scipy.interpolate import interp1d

class HRV():
    def __init__(self, rrtime, rrint):
        self.rrtime = rrtime
        self.rrint = rrint

        self.time_domain()
        self.freq_domain()

    def time_domain(self):
        sd = self.rrint[1:]-self.rrint[:-1]

        self.avgnn = self.rrint.mean()
        self.sdnn = self.rrint.std()
        self.rmssd = np.sqrt((sd**2).mean())
        self.sdsd = sd.std()
        self.nn50 = np.where(sd>50.)[0].size
        self.pnn50 = self.nn50/self.rrint.size
        self.nn20 = np.where(sd>20.)[0].size
        self.pnn20 = self.nn20/self.rrint.size

    def freq_domain(self):
        func = interp1d(self.rrtime, self.rrint, kind='cubic')
        irrt = np.arange(self.rrtime[0], self.rrtime[-1], 1./4.)
        irri = func(irrt)

        fx, px = scipy.signal.welch(irri,nperseg=120,fs=4.0)
        hf = px[np.logical_and(fx>=.15, fx<.40)]
        lf = px[np.logical_and(fx>=.04, fx<.15)]

        self.hf = sum(hf)
        self.lf = sum(lf)
        self.vlf = sum(px[np.logical_and(fx>=0., fx<.04)])
        self.hf_log = np.log(self.hf)
        self.lf_log = np.log(self.lf)
        self.vlf_log = np.log(self.vlf)
        self.hf_peak = fx[np.argmax(hf)]
        self.lf_peak = fx[np.argmax(lf)]
        self.hf_lf = self.lf/self.hf