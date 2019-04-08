.. _usage_physio:

.. testsetup::

    import numpy as np
    np.random.seed(1234)


The ``Physio`` data object
--------------------------

The primary funtionality of :py:mod:`peakdet` relies on its operations being
performed on physiological data loaded into a :py:class:`peakdet.Physio`
object. So, before we get into using :py:mod:`peakdet`, its best to understand
a little bit about this helper class!

All you need to create a :py:class:`~.Physio` object is a data array:

.. doctest::

    >>> import numpy as np
    >>> from peakdet import Physio
    >>> data = np.random.rand(5000)
    >>> phys = Physio(data)
    >>> print(phys)
    Physio(size=5000, fs=nan)

However, it is *strongly* recommended that you provide the sampling rate of the
data as well. Many functions in :py:mod:`peakdet` require this information:

.. doctest::

    >>> sampling_rate = 100.0
    >>> phys = Physio(data, fs=sampling_rate)
    >>> print(phys)
    Physio(size=5000, fs=100.0)

A :py:class:`~.Physio` object is designed to be lightweight, and mostly exists
to store raw physiological data and its corresponding sampling rate in the same
place. In most instances it can be treated like a one-dimensional
:py:class:`numpy.ndarray`; the underlying data can be accessed via slicing and
the object can be passed directly to most :py:mod:`numpy` functions:

.. doctest::

    >>> phys[:5]
    array([ 0.19151945,  0.62210877,  0.43772774,  0.78535858,  0.77997581])
    >>> np.mean(phys)
    0.49915239875191553

Beyond being a simple container, however, :py:class:`~.Physio` objects have a
few attributes that are of interest when working with real physiological data.
Importantly, they have a :py:attr:`~.Physio.history` that records all
operations performed on the data:

.. doctest::

    >>> from peakdet import operations
    >>> phys = operations.filter_physio(phys, cutoffs=0.1, method='lowpass')
    >>> phys.history
    [('filter_physio', {'cutoffs': 0.1, 'method': 'lowpass', 'order': 3})]

Moreover, if you perform peak finding on a :py:class:`~.Physio` object it will
store the indices of the detected :py:attr:`~.Physio.peaks` and
:py:attr:`~.Physio.troughs` alongside the object:

.. doctest::

    >>> phys = operations.peakfind_physio(phys)
    >>> phys.peaks
    array([ 477, 2120, 3253, 4128])
    >>> phys.troughs
    array([1413, 2611, 3756])

Next, we'll move on to how you can load your data into a :py:class:`~.Physio`
object in a more reproducible manner. Feel free to refer to the :ref:`api_ref`
for more information.
