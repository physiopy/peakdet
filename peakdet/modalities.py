# -*- coding: utf-8 -*-

import numpy as np
from loguru import logger


class HRModality:
    def iHR(self, step=1, start=0, end=None, TR=None):
        if end is None:
            end = self.rrtime[-1]

        mod = self.TR * (step // 2)
        time = np.arange(start - mod, end + mod + 1, self.TR, dtype="int")
        HR = np.zeros(len(time) - step)

        for tpoint in range(step, time.size):
            inds = np.logical_and(
                self.rrtime >= time[tpoint - step], self.rrtime < time[tpoint]
            )
            relevant = self.rrint[inds]

            if relevant.size == 0:
                continue
            HR[tpoint - step] = (60 / relevant).mean()

        return HR

    def meanHR(self):
        return np.mean(60 / self.rrint)


class ECG:
    flims = [5, 15.0]


class PPG:
    flims = 2.0


class RESP:
    flims = [0.05, 0.5]

    def RVT(self, start=0, end=None, TR=None):
        if end is None:
            end = self.rrtime[-1]

        pheight, theight = self.data[self.peakinds], self.data[self.troughinds]
        rvt = (pheight[:-1] - theight) / (np.diff(self.peakinds) / self.fs)
        rt = (self.peakinds / self.fs)[1:]

        time = np.arange(start, end + 1, self.TR, dtype="int")
        iRVT = np.interp(time, rt, rvt, left=rvt.mean(), right=rvt.mean())

        return iRVT
