# -*- coding: utf-8 -*-
"""
Functions and class for performing interactive editing of physiological data
"""

import functools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from peakdet import operations, utils


class _PhysioEditor():
    """
    Class for editing physiological data

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    """

    def __init__(self, data):
        # save reference to data and generate "time" for interpretable X-axis
        self.data = utils.check_physio(data, copy=True)
        fs = 1 if data.fs is None else data.fs
        self.time = np.arange(0, len(data.data) / fs, 1 / fs)

        # we need to create these variables in case someone doesn't "quit"
        # the plot appropriately (i.e., clicks X instead of pressing ctrl+q)
        self.deleted, self.rejected = set(), set()

        # make main plot objects
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, tight_layout=True)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheel)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        # two selectors for rejection (left mouse) and deletion (right mouse)
        reject = functools.partial(self.on_remove, reject=True)
        delete = functools.partial(self.on_remove, reject=False)
        self.span1 = SpanSelector(self.ax, reject, 'horizontal',
                                  button=1, useblit=True,
                                  rectprops=dict(facecolor='red', alpha=0.3))
        self.span2 = SpanSelector(self.ax, delete, 'horizontal',
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
        """ Quits editor """
        plt.close(self.fig)

    def on_key(self, event):
        """ Undoes last span select or quits peak editor """
        # accept both control or Mac command key as selector
        if event.key in ['ctrl+z', 'super+d']:
            self.undo()
        elif event.key in ['ctrl+q', 'super+d']:
            self.quit()

    def on_remove(self, xmin, xmax, *, reject):
        """ Removes specified peaks by either rejection / deletion """
        tmin, tmax = np.searchsorted(self.time, (xmin, xmax))
        pmin, pmax = np.searchsorted(self.data.peaks, (tmin, tmax))
        bad = np.arange(pmin, pmax, dtype=int)

        if len(bad) == 0:
            return

        if reject:
            rej, fcn = self.rejected, operations.reject_peaks
        else:
            rej, fcn = self.deleted, operations.delete_peaks

        # store edits in local history
        rej.update(self.data.peaks[bad].tolist())
        self.data = fcn(self.data, self.data.peaks[bad])
        self.plot_signals()

    def undo(self):
        """ Resets last span select peak removal """
        # check if last history entry was a manual reject / delete
        if self.data._history[-1][0] not in ['reject_peaks', 'delete_peaks']:
            return

        # pop off last edit and delete
        func, peaks = self.data._history.pop()

        if func == 'reject_peaks':
            self.data._metadata['reject'] = np.setdiff1d(
                self.data._metadata['reject'], peaks['remove']
            )
            self.rejected.difference_update(peaks['remove'])
        elif func == 'delete_peaks':
            self.data._metadata['peaks'] = np.insert(
                self.data._metadata['peaks'],
                np.searchsorted(self.data._metadata['peaks'], peaks['remove']),
                peaks['remove']
            )
            self.deleted.difference_update(peaks['remove'])

        self.data._metadata['troughs'] = utils.check_troughs(self.data,
                                                             self.data.peaks)
        self.plot_signals()
