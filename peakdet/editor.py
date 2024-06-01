# -*- coding: utf-8 -*-
"""Functions and class for performing interactive editing of physiological data."""

import functools

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import SpanSelector

from peakdet import operations, utils
from loguru import logger


class _PhysioEditor:
    """
    Class for editing physiological data.

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
        # Read if there is support data
        self.suppdata = data.suppdata

        # we need to create these variables in case someone doesn't "quit"
        # the plot appropriately (i.e., clicks X instead of pressing ctrl+q)
        self.deleted, self.rejected, self.included = set(), set(), set()

        # make main plot objects depending on supplementary data
        if self.suppdata is None:
            self.fig, self._ax = plt.subplots(
                nrows=1, ncols=1, tight_layout=True, sharex=True
            )
        else:
            self.fig, self._ax = plt.subplots(
                nrows=2,
                ncols=1,
                tight_layout=True,
                sharex=True,
                gridspec_kw={"height_ratios": [3, 2]},
            )

        self.fig.canvas.mpl_connect("scroll_event", self.on_wheel)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

        # Set axis handler
        self.ax = self._ax if self.suppdata is None else self._ax[0]

        # three selectors for:
        #    1. rejection (central mouse),
        #    2. addition (right mouse), and
        #    3. deletion (left mouse)
        delete = functools.partial(self.on_edit, method="delete")
        reject = functools.partial(self.on_edit, method="reject")
        insert = functools.partial(self.on_edit, method="insert")
        self.span2 = SpanSelector(
            self.ax,
            delete,
            "horizontal",
            button=1,
            useblit=True,
            rectprops=dict(facecolor="red", alpha=0.3),
        )
        self.span1 = SpanSelector(
            self.ax,
            reject,
            "horizontal",
            button=2,
            useblit=True,
            rectprops=dict(facecolor="blue", alpha=0.3),
        )
        self.span3 = SpanSelector(
            self.ax,
            insert,
            "horizontal",
            button=3,
            useblit=True,
            rectprops=dict(facecolor="green", alpha=0.3),
        )

        self.plot_signals(False)

    def plot_signals(self, plot=True):
        """Clear axes and plots data / peaks / troughs."""
        # don't reset x-/y-axis zooms on replot
        if plot:
            xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        else:
            xlim, ylim = (-5, None), (None, None)

        # clear old data + redraw, retaining x-/y-axis zooms
        self.ax.clear()
        self.ax.plot(
            self.time,
            self.data,
            "b",
            self.time[self.data.peaks],
            self.data[self.data.peaks],
            ".r",
            self.time[self.data.troughs],
            self.data[self.data.troughs],
            ".g",
        )

        if self.suppdata is not None:
            self._ax[1].plot(self.time, self.suppdata, "k", linewidth=0.7)
            self._ax[1].set_ylim(-0.5, 0.5)

        self.ax.set(xlim=xlim, ylim=ylim, yticklabels="")
        self.fig.canvas.draw()

    def on_wheel(self, event):
        """Move axis on wheel scroll."""
        (xlo, xhi), move = self.ax.get_xlim(), event.step * -10
        self.ax.set_xlim(xlo + move, xhi + move)
        self.fig.canvas.draw()

    def quit(self):
        """Quit editor."""
        plt.close(self.fig)

    def on_key(self, event):
        """Undo last span select or quits peak editor."""
        # accept both control or Mac command key as selector
        if event.key in ["ctrl+z", "super+d"]:
            self.undo()
        elif event.key in ["ctrl+q", "super+d"]:
            self.quit()

    def on_edit(self, xmin, xmax, *, method):
        """
        Edit peaks by rejection, deletion, or insert.

        Removes specified peaks by either rejection / deletion, OR
        Include one peak by finding the max in the selection.

        method accepts 'insert', 'reject', 'delete'
        """
        logger.debug("Edit")
        if method not in ["insert", "reject", "delete"]:
            raise ValueError(f'Action "{method}" not supported.')

        tmin, tmax = np.searchsorted(self.time, (xmin, xmax))
        pmin, pmax = np.searchsorted(self.data.peaks, (tmin, tmax))

        if method == "insert":
            tmp = np.argmax(self.data.data[tmin:tmax]) if tmin != tmax else 0
            newpeak = tmin + tmp
            if newpeak == tmin:
                self.plot_signals()
                return
        else:
            bad = np.arange(pmin, pmax, dtype=int)
            if len(bad) == 0:
                self.plot_signals()
                return

        if method == "reject":
            rej, fcn = self.rejected, operations.reject_peaks
        elif method == "delete":
            rej, fcn = self.deleted, operations.delete_peaks

        # store edits in local history & call function
        if method == "insert":
            self.included.add(newpeak)
            self.data = operations.add_peaks(self.data, newpeak)
        else:
            rej.update(self.data.peaks[bad].tolist())
            self.data = fcn(self.data, self.data.peaks[bad])

        self.plot_signals()

    def undo(self):
        """Reset last span select peak removal."""
        # check if last history entry was a manual reject / delete
        relevant = ["reject_peaks", "delete_peaks", "add_peaks"]
        if self.data._history[-1][0] not in relevant:
            return

        # pop off last edit and delete
        func, peaks = self.data._history.pop()

        if func == "reject_peaks":
            self.data._metadata["reject"] = np.setdiff1d(
                self.data._metadata["reject"], peaks["remove"]
            )
            self.rejected.difference_update(peaks["remove"])
        elif func == "delete_peaks":
            self.data._metadata["peaks"] = np.insert(
                self.data._metadata["peaks"],
                np.searchsorted(self.data._metadata["peaks"], peaks["remove"]),
                peaks["remove"],
            )
            self.deleted.difference_update(peaks["remove"])
        elif func == "add_peaks":
            self.data._metadata["peaks"] = np.delete(
                self.data._metadata["peaks"],
                np.searchsorted(self.data._metadata["peaks"], peaks["add"]),
            )
            self.included.remove(peaks["add"])
        self.data._metadata["troughs"] = utils.check_troughs(
            self.data, self.data.peaks, self.data.troughs
        )
        self.plot_signals()
