# peakdet
This package provide a Python interface for reproducible physiological data analysis

## Status
[![Build Status](https://travis-ci.org/rmarkello/peakdet.svg?branch=master)](https://travis-ci.org/rmarkello/peakdet)
[![Coverage Status](https://coveralls.io/repos/github/rmarkello/peakdet/badge.svg?branch=master)](https://coveralls.io/github/rmarkello/peakdet?branch=master)

## Table of Contents
If you know where you're going, feel free to jump ahead:
* [Purpose](#purpose)
    * [Overview](#overview)
    * [Background](#background)
    * [Development](#development)
* [Installation](#installation-and-setup)
* [Example usage](#usage)
* [How to get involved](#how-to-get-involved)
* [Credit](#credit)

## Purpose
#### Overview
This package is designed for use in the reproducible processing and analysis of physiological data, like those collected from respiration, pulse, or ECG monitors.

#### Background
Physiological data are messy and prone to artifact (e.g., movement in respiration and pulse, ectopic beats in ECG), and despite leaps and bounds in recent algorithms for processing these data many still require manual inspection of the waveforms to ensure such artifacts have been appropriately removed.
Largely because of this manual intervention step, understanding exactly what happened to go from "raw" data to processed or "analysis-ready" data can often be difficult.
This toolbox aims to provide a set of tools that will work with a variety of input data to reproducibly generate manually-corrected, analysis-ready physiological data.

#### Development
This package has largely been developed in the spare time of a single graduate student ([`@rmarkello`](https://github.com/rmarkello)), so while it would be :sparkles: amazing :sparkles: if anyone else finds it helpful, this package is not currently accepting requests for new features.
Contributions of new feature via are certainly welcome, but please first see our [contributing guidelines](CONTRIBUTING.md) for instructions on the preferred process to do so.

## Installation and setup
This package requires Python >= 3.5.
Assuming you have the correct version of Python installed, you can install this package by opening a terminal and running the following:

```bash
$ git clone https://github.com/rmarkello/peakdet.git
$ cd peakdet
$ python setup.py install
```

(Make sure to omit the `$` if copying and pasting these commands!)

## Usage
The API of `peakdet` is under active development, so it's not quite stable enough for example usage instructions.
If you're *super eager* to get started I would recommend creating an issue to let the developers know there's external interest in these sorts of things.
Otherwise, check back soon!

## How to get involved
We're thrilled to welcome new contributors!
If you're interesting in getting involved, you should start by reading our [contributing guidelines](CONTRIBUTING.md) and [code of conduct](CODE_OF_CONDUCT.md).

Once you're done with that, you can take a look at our list of active [issues](https://github.com/rmarkello/pyls/issues) and let us know if there's something you'd like to begin working on.

If you've found a bug, are experiencing a problem, or have a question, create a new issue with some information about it!

## Credit
Many of the behind-the-scenes functions in `peakdet` are imperfect translations of code from the [`PhysIO`](https://github.com/translationalneuromodeling/tapas/tree/master/PhysIO) MATLAB toolbox, and the toolbox is therefore licensed under the [GPLv3](LICENSE).
Please be sure to cite their paper if you use this tool ([Kasper et al., 2017](http://www.sciencedirect.com/science/article/pii/S016502701630259X)).
