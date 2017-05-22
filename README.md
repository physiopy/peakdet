peakdet
-------
Physiological peak detection in Python

## Status
[![Build Status](https://travis-ci.org/rmarkello/peakdet.svg?branch=master)](https://travis-ci.org/rmarkello/peakdet)
[![Coverage Status](https://coveralls.io/repos/github/rmarkello/peakdet/badge.svg?branch=master)](https://coveralls.io/github/rmarkello/peakdet?branch=master)

## Overview

Peakdet is designed for use in analysis and interpretation of physiological recordings (e.g., respiration, pulse, and ECG).

## Installation

Cloning the repo from GitHub and running the usual `python setup.py install` should work.

## Usage
A short, illustrative use case. Similar functionality can be found for ECG (electrocardiogram) and RESP (respiration) data; simply replace peakdet.PPG below with the appropriate acronym (i.e., peakdet.ECG, peakdet.RESP).

```python
>>> import peakdet
>>> datafile, samplerate = 'PPG.1D', 40.

# create an instance of a PPG waveform and plot it
>>> ppg = peakdet.PPG(datafile, samplerate)
>>> ppg.plot()

# interpolate data to 1000 Hz
>>> ppg.interpolate(1000/ppg.fs)

# let's say we don't want that -- we can reset things!
>>> ppg.reset(hard=True)

# perform peak-finding on the waveform and re-plot the data
#     thresh: determines relative height threshold
#     dist:   determines minimum distance between adjacent peaks (in samples)
>>> ppg.get_peaks(thresh=0.4, dist=20)
>>> ppg.plot()

# indices of the detected peaks
>>> ppg.peakinds
array([   16,    53,    90,   127,   162,   198,   238,   277,   315,
         348,   384,   419,   454,   489,   523,   558,   595,   633,
         ...,
         24418, 24455])

# indices of the detected troughs
>>> ppg.troughinds
array([   38,    76,   114,   149,   184,   223,   262,   301,   335,
         370,   405,   440,   476,   509,   545,   581,   619,   655,
         ...,
         24137, 24171, 24204, 24237, 24271, 24304, 24336, 24369, 24404, 24441])

# let's create a time series of instantaneous HR, sampled at 3 second bins
# this might be useful in a time series regression
>>> ppg.TR = 3.0  # set the default bin
>>> ppg.iHR()
array([ 64.86486486,  65.02574003,  65.80787633,  67.93650794,
        68.14898933,  67.51727804,  69.32178932,  67.2223484 ,
        ...,
        70.11459129,  70.70707071,  72.22593583,  68.72118872])
```

## Credit

Many of the behind-the-scenes functions in `peakdet` are translated from the [`physIO`](http://www.translationalneuromodeling.org/tnu-checkphysretroicor-toolbox/) MATLAB toolbox. Consider this an imperfect translation and wrapping of their code, and cite their code [(Kasper et al., 2017)](http://www.sciencedirect.com/science/article/pii/S016502701630259X).
