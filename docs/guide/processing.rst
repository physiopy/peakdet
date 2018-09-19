.. _usage_processing:

Processing data
---------------

There are a few common processing steps often performed when working with
physiological data:

    1. :ref:`usage_proc_interp`,
    2. :ref:`usage_proc_filtering`,
    3. :ref:`usage_proc_peakdet`,
    4. :ref:`usage_proc_visual`, and
    5. :ref:`usage_proc_artifact`

We have already seen that :py:mod:`peakdet.operations` has functions to perform
a few of these steps, but it is worth going into all of them with a bit more
depth.

.. _usage_proc_interp:

Interpolation
^^^^^^^^^^^^^

Raw data can often be collected at a sampling rate above what is biologically
meaningful. For example, human respiration is relatively slow, so acquiring it
at, for example, 250 Hz is often more than sufficient; indeed, when it is
acquired at a higher rate it can be quite noisy. In this case, we might want to
decimate the data.

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
