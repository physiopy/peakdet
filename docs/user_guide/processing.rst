.. _usage_processing:

Processing physiological data
-----------------------------

There are a few common processing steps often performed when working with
physiological data:

    1. :ref:`usage_proc_interp`,
    2. :ref:`usage_proc_filtering`,
    3. :ref:`usage_proc_peakdet`,
    4. :ref:`usage_proc_visual`, and
    5. :ref:`usage_proc_artifact`

We have already seen that :py:mod:`peakdet.operations` has functions to perform
a few of these steps, but it is worth going into all of them in a bit more
detail:

.. _usage_proc_interp:

Interpolation
^^^^^^^^^^^^^

Raw data can often be collected at a sampling rate above what is biologically
meaningful. For example, human respiration is relatively slow, so acquiring it
at, for example, 250 Hz is often more than sufficient; when it is acquired at a
higher rate it can be quite noisy. In this case, we might want to decimate the
data to a lower sampling rate, which can be done with
:py:func:`~.operations.interpolate_physio`:

.. doctest::

    >>> from peakdet import load_physio, operations
    >>> data = load_physio('RESP.csv', fs=1000.)
    >>> print(data)
    Physio(size=24000, fs=1000.0)
    >>> data = operations.interpolate_physio(data, target_fs=250.)
    >>> print(data)
    Physio(size=6000, fs=250.0)

Data can also be upsampled via interpolation, though care must be taken in
interpreting the results of such data:

.. doctest::

    >>> data = load_physio('PPG.csv', fs=250.)
    >>> print(data)
    Physio(size=24000, fs=250.0)
    >>> data = operations.interpolate_physio(data, target_fs=1000.)
    >>> print(data)
    Physio(size=96000, fs=1000.0)

.. _usage_proc_filtering:

Temporal filtering
^^^^^^^^^^^^^^^^^^

.. _usage_proc_peakdet:

Peak detection
^^^^^^^^^^^^^^

.. _usage_proc_visual:

Visual inspection
^^^^^^^^^^^^^^^^^

.. _usage_proc_artifact:

Artifact rejection
^^^^^^^^^^^^^^^^^^
