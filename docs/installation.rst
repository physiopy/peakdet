.. _installation:

============
Installation
============

Requirements
------------

``peakdet`` requires python 3.6 or above, as well as the modules:

.. literalinclude:: ../setup.cfg
   :lines: 28-30
   :dedent: 4

Linux and mac installation
--------------------------
The most convenient option is to use ``pip``, as it allows you to automatically download and install the package from `PyPI repository <https://pypi.org/project/peakdet/>`_ and facilitates upgrading or uninstalling it.

Install with ``pip``
^^^^^^^^^^^^^^^^^^^^

.. note::
    The following instructions are provided assuming that python 3 is **not** your default version of python.
    If it is, you might need to use ``pip`` instead of ``pip3``, although some OSs do adopt ``pip3`` anyway.
    If you want to check, type ``python --version`` in a terminal.

To install ``peakdet`` along with the basic required modules just run::

    pip3 install phys2bids
    
You can now proceed to check your installation and start using ``peakdet``!

Check your installation!
^^^^^^^^^^^^^^^^^^^^^^^^

Through the terminal, type the command::

    pip show peakdet

Through python script, type the commands::

    import peakdet
    print(peakdet.__version__)

If your output is: ``0.2.0rc1`` or similar, ``peakdet`` is ready to be used.

Windows installation
--------------------

First of all let's check you have python installed. Open a windows power shell window in **admin mode** and type::

    python --version

In case you don't have it, either install it by clicking on the link for the *Latest python 3 Release* `here <https://www.python.org/downloads/windows/>`_ or type the command::

    python

It will redirect you to the windows store python install (in the creation of this tutorial the newest version of python was 3.11).

.. warning::
    ``peakdet`` supports Python 3.6 and later versions. We can't guarantee it will work if you use python 2.

Once python is installed, you can follow the instructions to install ``peakdet`` reported `above <#install-with-pip>`_

.. note::
    Remember to open a terminal in **admin mode** to install libraries!