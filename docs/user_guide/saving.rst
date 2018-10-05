.. _usage_saving:

.. testsetup::

    from peakdet import load_physio, operations
    data = load_physio('PPG.csv', fs=25.0)
    data = operations.interpolate_physio(data, target_fs=250.0)
    data = operations.filter_physio(data, cutoffs=1.0, method='lowpass')
    data = operations.peakfind_physio(data, thresh=0.1, dist=100)

Reproducibly saving data
------------------------

Once you've gone through preprocessing and manually editing your data, you'll
likely want to save your work. :py:mod:`peakdet` provides two ways to save your
outputs, depending on your data storage needs.

Duplicating data
^^^^^^^^^^^^^^^^

If you don't mind storing multiple copies of your data, you can simply save the
:py:class:`~.Physio` object directly using :py:func:`peakdet.save_physio`:

.. doctest::

    >>> from peakdet import save_physio
    >>> path = save_physio('out.phys', data)

If later on you want to reload the processed data you can do so:

.. doctest::

    >>> from peakdet import load_physio
    >>> data = load_physio('out.phys')

.. note::

    :py:func:`peakdet.save_physio` uses :py:func:`numpy.savez_compressed` to
    save the data objects, meaning the generated files can actually be quite a
    bit larger than the original data, themselves!

Saving history
^^^^^^^^^^^^^^

If you loaded all your data using the IO functions contained in
:py:mod:`peakdet` then your :py:class:`~.Physio` objects should have a
complete :py:attr:`~.Physio.history`. If that's the case, you can avoid saving
a duplicate copy of your entire data structure and just save the history! To do
this we can use :py:func:`peakdet.save_history`:

.. doctest::

    >>> from peakdet import save_history
    >>> path = save_history('out.json', data)

The history is saved as a `JSON <https://en.wikipedia.org/wiki/JSON>`_ file. If
you're unfamiliar, JSON files are plain text files that can store lists and
dictionaries–which is exactly what the history is!

We can then load in the history (and recreate the :py:class:`~.Physio` object
it described) with :py:func:`peakdet.load_history`:

.. doctest::

    >>> from peakdet import load_history
    >>> data = load_history('out.json')

The ``data`` object contains all the processing (including manual edits!) that
were performed on the original physiological data.

While the saved history file (in this example, ``out.json``) can be stored
anywhere (next to the raw data file typically makes sense!), extra care must be
taken when loading it back in. Because the history file contains a path to the
raw data file, you must ensure that it is loaded with :py:func:`~.load_history`
from the same directory in which the raw data were originally loaded.

Let's say that we have a directory tree that looks like the following:

.. code-block:: bash

    ./experiment
    ├── code/
    │   └── preprocess.py
    └── data/
        └── sub-001/
            └── PPG.csv

We navigate to this directory (``cd experiment``) and run ``python
code/preprocess.py``, which generates a history file:

.. code-block:: bash

    ./experiment
    ├── code/
    │   └── preprocess.py
    └── data/
        └── sub-001/
            ├── PPG.csv
            └── PPG_history.json

Now, say we zip the entire ``experiment`` directory to send to a collaborator
who wants to run some analyses on our processed data. If they want to
regenerate the :py:class:`~.Physio` objects we created from the saved history
files, they must call :py:func:`~.load_history` from within the ``experiment``
directory. Calling it from anywhere else in the directory tree will result in
a ``FileNotFoundError`` with a suggestion as to why the call failed.

.. note::

    In order to be able to reproducibly regenerate data using history files,
    you need to ensure that you load your data using relative paths from the
    get-go!
