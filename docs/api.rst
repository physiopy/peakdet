.. _api_ref:

API
===

.. py:module:: peakdet

Physiological data
------------------

.. autoclass:: peakdet.Physio

Loading data
------------

.. autofunction:: peakdet.load_physio
.. autofunction:: peakdet.load_history
.. autofunction:: peakdet.load_rtpeaks

Processing data
---------------

.. automodule:: peakdet.operations
   :members: interpolate_physio, filter_physio, peakfind_physio, plot_physio, edit_physio

Saving data
-----------

.. autofunction:: peakdet.save_physio
.. autofunction:: peakdet.save_history

Derived metrics
---------------

.. autoclass:: peakdet.HRV
