peakdet
-------
Physiological peak detection in Python

## Status
[![Build Status](https://travis-ci.org/rmarkello/peakdet.svg?branch=master)](https://travis-ci.org/rmarkello/peakdet)
[![Coverage Status](https://coveralls.io/repos/github/rmarkello/peakdet/badge.svg?branch=master)](https://coveralls.io/github/rmarkello/peakdet?branch=master)

## Overview

Peakdet is designed for use in analysis and interpretation of human physiological recordings (e.g., respiration, pulse, and ECG); however, it can be adapted for non-human recordings, too.

## Installation

Cloning the repo from GitHub and running the usual `python setup.py install` should work.

## Usage
A not-so-short, somewhat-illustrative use case. Similar functionality can be found for ECG (electrocardiogram) and RESP (respiration) data; simply replace peakdet.PPG below with the appropriate acronym (i.e., peakdet.ECG, peakdet.RESP).

```python
>>> import peakdet
>>> datafile, samplerate = 'PPG.1D', 40.

# create an instance of a PPG waveform and plot it
>>> ppg = peakdet.PPG(datafile, samplerate)
>>> ppg.plot()

# interpolate data to 1000 Hz (note that the arg here is a multiplying factor -- i.e., the end sampling rate is samplerate (40) * 25)
>>> ppg.interpolate(25)

# lowpass filter the data (cutoff = 2.0 Hz)
>>> ppg.lowpass(2.0)

# let's say we don't want that -- we can reset things! the `hard=True` kwarg
# ensures that interpolation is reset; by default, only filtering is reset
# it's worth noting that the PPG, ECG, and RESP classes have built-in filtering
# based on the expected shape of these waveforms. if that isn't desired, you
# should use ppg.PeakFinder in lieu of the modality classes
>>> ppg.reset(hard=True)

# perform peak-finding on the waveform
#     thresh : determines relative height threshold;
#              the PPG/ECG/RESP classes have default thresholds that have been
#              determined to work most of the time for those waveforms
#     dist   : determines minimum distance between adjacent peaks (in samples)
#              if not provided, the program will do its best to approximate a
#              good distance (i.e., this does not default to 0)
>>> ppg.get_peaks(thresh=0.4, dist=20)

# replotting the data will show detected peaks (red) and troughs (green)
>>> ppg.plot()

# we can also get the indices of the detected peaks
>>> ppg.peakinds
array([   16,    53,    90,   127,   162,   198,   238,   277,   315, ...])

# and the indices of the detected troughs
>>> ppg.troughinds
array([   38,    76,   114,   149,   184,   223,   262,   301,   335, ...])

# finally, we can create a instantaneous heart rate time series.
# setting the `TR` attribute ensures that the method knows how to bin the data;
# that is, it will calculate the average iHR in 3s bins over the entire time
# course
>>> ppg.TR = 3.0  # set the default bin
>>> ppg.iHR()
array([ 64.86486486,  65.02574003,  65.80787633,  67.93650794, ...])
```

## Credit

Many of the behind-the-scenes functions in `peakdet` are translated from the [`physIO`](http://www.translationalneuromodeling.org/tnu-checkphysretroicor-toolbox/) MATLAB toolbox. Consider this an imperfect translation and wrapping of their code, and cite their code if you use this tool ([Kasper et al., 2017](http://www.sciencedirect.com/science/article/pii/S016502701630259X)).
