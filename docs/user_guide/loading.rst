.. _usage_loading:

Reproducibly loading data
-------------------------

In order to ensure that a data analysis pipeline with :py:mod:`peakdet` is
fully reproducible from start to finish, it is recommended that you load data
with the built-in :py:mod:`peakdet` IO functions.

The :py:meth:`peakdet.load_physio` function is the most simple of these
functions, and accepts data stored as single-column text file. For example, if
we have a file `ECG.csv` that we might normally load with :py:mod:`numpy`:

.. doctest::

    >>> import numpy as np
    >>> np.loadtxt('ECG.csv')
    array([ 1.66656,  1.53076,  1.38153, ..., -0.05188, -0.05249, -0.05554])

we can instead load it into a :py:class:`~.Physio` object in one step with:

.. doctest::

    >>> from peakdet import load_physio
    >>> ecg = load_physio('ECG.csv', fs=1000.)
    >>> print(ecg)
    Physio(size=44611, fs=1000.0)
    >>> ecg.data
    array([ 1.66656,  1.53076,  1.38153, ..., -0.05188, -0.05249, -0.05554])

This way, the loading of the data is retained in the object's history:

.. doctest::

    >>> ecg.history
    [('load_physio', {'data': 'ECG.csv', 'fs': 1000.0, 'dtype': None, 'history': None})]

There are also a number of functions for loading data from "standard" formats.
For example, if your data were collected using the `rtpeaks <https://github.com
/rmarkello/rtpeaks>`_ module, it might look like this:

.. doctest::

    >>> import pandas as pd
    >>> pd.read_csv('rtpeaks.csv').head()
       time  channel1  channel2  channel9
    0   1.0  4.984436  0.020752 -0.333862
    1   2.0  4.984131  0.021057 -0.328979
    2   3.0  4.984131  0.021057 -0.325623
    3   4.0  4.984436  0.021057 -0.323792
    4   5.0  4.983826  0.025024 -0.319519

Instead, you can load it with :py:meth:`peakdet.load_rtpeaks` so that it is
recorded in the object's history:

.. doctest::

    >>> from peakdet import load_rtpeaks
    >>> ecg = load_rtpeaks('rtpeaks.csv', fs=1000., channel=9)
    >>> print(ecg)
    Physio(size=40, fs=1000.0)
    >>> ecg[:5]
    array([-0.3338623 , -0.32897949, -0.32562256, -0.3237915 , -0.31951904])
    >>> ecg.history
    [('load_rtpeaks', {'channel': 9', 'fname': 'rtpeaks.csv', 'fs': 1000.0})]
