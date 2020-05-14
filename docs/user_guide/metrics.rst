.. _usage_metrics:

.. testsetup::

    from peakdet import load_physio, operations
    data = load_physio('PPG.csv', fs=25.0)
    data = operations.interpolate_physio(data, target_fs=250.0)
    data = operations.filter_physio(data, cutoffs=1.0, method='lowpass')
    data = operations.peakfind_physio(data, thresh=0.1, dist=100)
    data = operations.reject_peaks(data, [81441, 160786, 163225])

Deriving physiological metrics
------------------------------

Once you've processed your physiological data, chances are you want to use it
to calculate some derived metrics. :py:mod:`peakdet` currently only support
metrics related to `heart rate variability <https://en.wikipedia.org/wiki/
Heart_rate_variability>`_, accessible through the :py:class:`peakdet.HRV`
class.

Assuming you have a :py:class:`~.Physio` object that contains some sort of
heart data and you've performed peak detection on it, you can provide it
directly to the :py:class:`~.HRV` class:

.. doctest::

    >>> from peakdet import HRV
    >>> metrics = HRV(data)
    >>> print(f'{metrics.rmssd:.2f} ms')
    26.61 ms

The :py:class:`~.HRV` class contains many common heart rate variability metrics
including the root mean square of successive differences, as shown above. It
also calculates the R-R interval time series from the provided data, which can
be accessed via the :py:attr:`~.HRV.rrint` attribute. The corresponding
:py:attr:`.HRV.rrtime` attribute details the times at which these intervals
occurred.

Take a look at the :ref:`api_ref` for more information.
