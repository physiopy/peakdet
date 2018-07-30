# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from peakdet import physio, utils


class _PhysioEditor():
    """ Class for editing physiological data

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    """

    def __init__(self, data):
        if not isinstance(data, physio.Physio):
            raise TypeError('Input must be a Physio instance')
        # save reference to data
        self.data = data
        fs = 1 if data.fs is None else data.fs
        self.time = np.arange(0, data.size / fs, 1. / fs)
        # make main plot objects
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, tight_layout=True)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheel)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        # two selectors for rejection (left mouse) / deletion (right mouse)
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
        lim, move = self.ax.get_xlim(), event.step * -10
        self.ax.set_xlim(lim[0] + move, lim[1] + move)
        self.fig.canvas.draw()

    def on_key(self, event):
        """ Undoes last span select or quits peak editor """
        if event.key == 'ctrl+z':
            self.undo()
        elif event.key == 'ctrl+q':
            plt.close(self.fig)

    def on_reject(self, xmin, xmax):
        """ Manually removes physio peaks on span select """
        rej = np.arange(*np.searchsorted(self.data.peaks,
                                         np.searchsorted(self.time,
                                                         (xmin, xmax))),
                        dtype=int)
        if len(self.data.peaks[rej]) == 0:
            return
        self.data._history.append(('manual_reject',
                                   self.data.peaks[rej].tolist()))
        self.data._metadata.reject = np.append(self.data._metadata.reject,
                                               self.data.peaks[rej])
        self.data._metadata.troughs = utils.check_troughs(self.data,
                                                          self.data.peaks,
                                                          self.data.troughs)
        self.plot_signals()

    def on_delete(self, xmin, xmax):
        """ Manually delete physio peaks on span select """
        rej = np.arange(*np.searchsorted(self.data.peaks,
                                         np.searchsorted(self.time,
                                                         (xmin, xmax))),
                        dtype=int)
        if len(self.data.peaks[rej]) == 0:
            return
        self.data._history.append(('manual_delete',
                                   self.data.peaks[rej].tolist()))
        self.data._metadata.peaks = np.delete(self.data._metadata.peaks, rej)
        self.data._metadata.troughs = utils.check_troughs(self.data,
                                                          self.data.peaks,
                                                          self.data.troughs)
        self.plot_signals()

    def undo(self):
        """ Resets last span select peak removal """
        # check if last history entry was a manual reject / delete
        if len(self.data.history) == 0:
            return
        elif self.data.history[-1][0] not in physio._ACCEPTED_HISTORY:
            return
        # pop off last edit
        func, peaks = self.data.history.pop()
        if func == 'manual_reject':
            self.data._metadata.reject = np.setdiff1d(
                self.data._metadata.reject, peaks
            )
        elif func == 'manual_delete':
            self.data._metadata.peaks = np.insert(
                self.data._metadata.peaks,
                np.searchsorted(self.data._metadata.peaks, peaks),
                peaks
            )
        else:
            raise ValueError('This should never happen.')
        self.data._metadata.troughs = utils.check_troughs(self.data,
                                                          self.data.peaks,
                                                          self.data.troughs)
        self.plot_signals()


def delete_peaks(data, delete):
    pass


def reject_peaks(data, reject):
    pass
