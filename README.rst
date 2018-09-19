peakdet: A toolbox for physiological peak detection analyses
============================================================

This package is designed for use in the reproducible processing and analysis of
physiological data, like those collected from respiratory belts, pulse
photoplethysmography, or electrocardiogram (ECG/EKG) monitors.

.. image:: https://travis-ci.org/rmarkello/peakdet.svg?branch=master
   :target: https://travis-ci.org/rmarkello/peakdet
.. image:: https://codecov.io/gh/rmarkello/peakdet/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/rmarkello/peakdet
.. image:: https://readthedocs.org/projects/peakdet/badge/?version=latest
   :target: http://peakdet.readthedocs.io/en/latest
.. image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0

.. _overview:

Overview
--------

Physiological data are messy and prone to artifact (e.g., movement in
respiration and pulse, ectopic beats in ECG). Despite leaps and bounds in
recent algorithms for processing these data there still exists a need for
manual inspection to ensure such artifacts have been appropriately removed.
Because of this manual intervention step, understanding exactly what happened
to go from "raw" data to "analysis-ready" data can often be difficult or
impossible.

This toolbox, ``peakdet``, aims to provide a set of tools that will work with a
variety of input data to reproducibly generate manually-corrected, analysis-
ready physiological data. If you'd like more information about the package,
including how to install it and some example instructions on its use, check out
our `documentation <https://peakdet.readthedocs.io>`_!

.. _development:

Development and getting involved
--------------------------------

This package has been largely developed in the spare time of a single graduate
student (`@rmarkello <https://github.com/rmarkello>`_) with help from some
incredible `contributors <https://github.com/rmarkello/peakdet/graphs/
contributors>`_. While it would be |sparkles| amazing |sparkles| if anyone else
finds it helpful, given the limited time constraints of graduate school, the
current package is not currently accepting requests for new features.

However, if you're interested in getting involved in the project, we're
thrilled to welcome new contributors! You should start by reading our
`contributing guidelines <https://github.com/rmarkello/peakdet/blob/master/
CONTRIBUTING.md>`_ and `code of conduct <https://github.com/rmarkello/peakdet/
blob/master/CODE_OF_CONDUCT.md>`_. Once you're done with that, take a look at
our `issues <https://github.com/rmarkello/peakdet/issues>`_ to see if there's
anything you might like to work on. Alternatively, if you've found a bug, are
experiencing a problem, or have a question, create a new issue with some
information about it!

.. _acknowledgments:

Acknowledgments
---------------

While this package was initially created in 2016, some of the behind-the-scenes
functions in the project were adopted from the `PhysIO <https://github.com/
translationalneuromodeling/tapas/tree/master/PhysIO>`_ MATLAB toolbox. As such,
if you use this code it would be good to (1) provide a link back to the
``peakdet`` repository with the version of the code used, and (2) cite `their
paper <http://www.sciencedirect.com/science/article/pii/S016502701630259X>`_:

.. [1] Kasper, L., Bollmann, S., Diaconescu, A. O., Hutton, C., Heinzle, J.,
   Iglesias, S., ... & Stephan, K. E. (2017). The PhysIO toolbox for modeling
   physiological noise in fMRI data. Journal of Neuroscience Methods, 276,
   56-72.

.. _licensing:

License Information
-------------------

This codebase is licensed under the GNU General Public License version 3.
The full license can be found in the `LICENSE <https://github.com/rmarkello/
peakdet/blob/master/LICENSE>`_ file in the ``peakdet`` distribution.

All trademarks referenced herein are property of their respective holders.

.. |sparkles| replace:: ✨
