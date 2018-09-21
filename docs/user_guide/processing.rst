.. _usage_processing:

.. testsetup::

    from peakdet import load_physio, operations

Processing physiological data
-----------------------------

There are a few common processing steps often performed when working with
physiological data:

    1. :ref:`usage_proc_visual`,
    2. :ref:`usage_proc_interp`,
    3. :ref:`usage_proc_filtering`,
    4. :ref:`usage_proc_peakdet`, and
    5. :ref:`usage_proc_artifact`

We have already seen that :py:mod:`peakdet.operations` has functions to perform
a few of these steps, but it is worth going into all of them in a bit more
detail:


.. _usage_proc_visual:

Visual inspection
^^^^^^^^^^^^^^^^^

One of the first steps to do with raw data is visually inspect it. No amount of
processing can fix bad data, and so it's good to check that your data quality
is appropriate before continuing. Plotting data can be achieved with
:py:func:`~.operations.plot_physio`; for now, this will simply plot the raw
waveform, but we'll see later how this function has some added benefits:

.. plot::
    :format: doctest
    :context: close-figs

    >>> from peakdet import load_physio, operations
    >>> data = load_physio('RESP.csv', fs=1000.0)
    >>> ax = operations.plot_physio(data)

This data looks good to go!

.. _usage_proc_interp:

Interpolation
^^^^^^^^^^^^^

Raw data can often be collected at a sampling rate above what is biologically
meaningful. For example, human respiration is relatively slow, so acquiring it
at, for example, 250 Hz is often more than sufficient; when it is acquired at a
higher rate it can be quite noisy. In this case, we might want to interpolate
(or decimate) the data to a lower sampling rate, which can be done with
:py:func:`~.operations.interpolate_physio`:

.. plot::
    :format: doctest
    :context: close-figs

    >>> data = load_physio('RESP.csv', fs=1000.)
    >>> print(data)
    Physio(size=24000, fs=1000.0)
    >>> data = operations.interpolate_physio(data, target_fs=250.)
    >>> print(data)
    Physio(size=6000, fs=250.0)

Data can also be upsampled via interpolation, though care must be taken in
interpreting the results of such a procedure:

.. plot::
    :format: doctest
    :context: close-figs

    >>> data = load_physio('PPG.csv', fs=25.0)
    >>> print(data)
    Physio(size=24000, fs=25.0)
    >>> data = operations.interpolate_physio(data, target_fs=250.0)
    >>> print(data)
    Physio(size=240000, fs=250.0)

.. _usage_proc_filtering:

Temporal filtering
^^^^^^^^^^^^^^^^^^

Once our data is at an appropriate sampling rate, we may want to apply a
temporal filter with :py:func:`~.operations.filter_physio`. This function
supports lowpass, highpass, bandpass, and bandstop filters with user-specified
frequency cutoffs. First, let's take a look at our interpolated PPG data:

.. plot::
    :format: doctest
    :context: close-figs

    >>> ax = operations.plot_physio(data)
    >>> ax.set_xlim(0, 10)  # doctest: +SKIP

If we're going to do peak detection, it would be great to get rid of the venous
pulsations in the waveform to avoid potentially picking them up. If we apply a
lowpass filter with a 1.0 Hz cutoff we can do just that:

.. plot::
    :format: doctest
    :context: close-figs

    >>> data = operations.filter_physio(data, cutoffs=1.0, method='lowpass')
    >>> ax = operations.plot_physio(data)
    >>> ax.set_xlim(0, 10)  # doctest: +SKIP

.. _usage_proc_peakdet:

Peak detection
^^^^^^^^^^^^^^

.. _usage_proc_artifact:

Artifact rejection
^^^^^^^^^^^^^^^^^^
