# -*- coding: utf-8 -*-
"""
Functions and class for performing interactive editing of physiological data
"""

import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from peakdet import physio, utils


class _PhysioEditor():
    """
    Class for editing physiological data

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    """

    def __init__(self, data):
        if not isinstance(data, physio.Physio):
            raise TypeError('Input must be a Physio instance')

        # save reference to data and generate "time" for interpretable X-axis
        self.data = data
        fs = 1 if data.fs is None else data.fs
        self.time = np.arange(0, len(data.data) / fs, 1 / fs)

        # we're going to store all the deletions / rejections in history
        self.history = []
        # we need to create these variables in case someone doesn't "quit"
        # the plot appropriately (i.e., clicks X instead of pressing ctrl+q)
        self.deleted = self.rejected = []

        # make main plot objects
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, tight_layout=True)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheel)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        # two selectors for rejection (left mouse) and deletion (right mouse)
        self.span1 = SpanSelector(self.ax, self.on_reject, 'horizontal',
                                  button=1, useblit=True,
                                  rectprops=dict(facecolor='red', alpha=0.3))
        self.span2 = SpanSelector(self.ax, self.on_delete, 'horizontal',
                                  button=3, useblit=True,
                                  rectprops=dict(facecolor='blue', alpha=0.3))

        self.plot_signals(False)

    def plot_signals(self, plot=True):
        """ Clears axes and plots data / peaks / troughs """
        # don't reset x-/y-axis zooms on replot
        if plot:
            xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        else:
            xlim, ylim = (-5, None), (None, None)

        # clear old data + redraw, retaining x-/y-axis zooms
        self.ax.clear()
        self.ax.plot(self.time, self.data, 'b',
                     self.time[self.data.peaks],
                     self.data[self.data.peaks], '.r',
                     self.time[self.data.troughs],
                     self.data[self.data.troughs], '.g')
        self.ax.set(xlim=xlim, ylim=ylim, yticklabels='')
        self.fig.canvas.draw()

    def on_wheel(self, event):
        """ Moves axis on wheel scroll """
        (xlo, xhi), move = self.ax.get_xlim(), event.step * -10
        self.ax.set_xlim(xlo + move, xhi + move)
        self.fig.canvas.draw()

    def quit(self):
        """ Quits editor and consolidates manual edits"""
        # clean up all the deleted / rejected entries
        deleted, rejected = [], []
        for (func, inp) in self.history:
            if func == 'reject_peaks':
                rejected.append(inp['remove'])
            elif func == 'delete_peaks':
                deleted.append(inp['remove'])
        # generate list of deleted / rejected
        self.rejected = list(itertools.chain.from_iterable(rejected))
        self.deleted = list(itertools.chain.from_iterable(deleted))
        plt.close(self.fig)

    def on_key(self, event):
        """ Undoes last span select or quits peak editor """
        # accept both control or Mac command key as selector
        if event.key in ['ctrl+z', 'super+d']:
            self.undo()
        elif event.key in ['ctrl+q', 'super+d']:
            self.quit()

    def on_reject(self, xmin, xmax):
        """ Manually removes physio peaks on span select """
        bad = np.arange(*np.searchsorted(self.data.peaks,
                                         np.searchsorted(self.time,
                                                         (xmin, xmax))),
                        dtype=int)
        if len(bad) == 0:
            return
        self.data, call = reject_peaks(self.data, self.data.peaks[bad])
        self.history += [call]
        self.plot_signals()

    def on_delete(self, xmin, xmax):
        """ Manually delete physio peaks on span select """
        bad = np.arange(*np.searchsorted(self.data.peaks,
                                         np.searchsorted(self.time,
                                                         (xmin, xmax))),
                        dtype=int)
        if len(bad) == 0:
            return
        self.data, call = delete_peaks(self.data, self.data.peaks[bad])
        self.history += [call]
        self.plot_signals()

    def undo(self):
        """ Resets last span select peak removal """
        # check if last history entry was a manual reject / delete
        if len(self.history) == 0:
            return
        # pop off last edit and delete
        func, peaks = self.history.pop()
        if func == 'reject_peaks':
            self.data._metadata.reject = np.setdiff1d(
                self.data._metadata.reject, peaks['remove']
            )
        elif func == 'delete_peaks':
            self.data._metadata.peaks = np.insert(
                self.data._metadata.peaks,
                np.searchsorted(self.data._metadata.peaks, peaks['remove']),
                peaks['remove']
            )

        self.data._metadata.troughs = utils.check_troughs(self.data,
                                                          self.data.peaks,
                                                          self.data.troughs)
        self.plot_signals()


def delete_peaks(data, remove, copy=False):
    """
    Deletes peaks in `remove` from peaks stored in `data`

    Parameters
    ----------
    data : Physio_like
    remove : array_like
    copy : bool, optional
        Whether to delete peaks on `data` in-place. Default: False

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=copy)
    data._metadata.peaks = np.setdiff1d(data._metadata.peaks, remove)
    data._metadata.troughs = utils.check_troughs(data, data.peaks,
                                                 data.troughs)

    return data, utils._get_call()


def reject_peaks(data, remove, copy=False):
    """
    Marks peaks in `remove` as rejected in `data`

    Parameters
    ----------
    data : Physio_like
    remove : array_like
    copy : bool, optional
        Whether to reject peaks on `data` in-place. Default: False

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=copy)
    data._metadata.reject = np.append(data._metadata.reject, remove)
    data._metadata.troughs = utils.check_troughs(data, data.peaks,
                                                 data.troughs)

    return data, utils._get_call()
