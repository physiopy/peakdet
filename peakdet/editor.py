# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from peakdet import physio


def edit_physio(data):
    """
    Returns interactive physio editor for `data`

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    """

    return PhysioEditor(data)


class PhysioEditor():
    """ Class for editing physiological data

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited
    """

    def __init__(self, data, _debug=False, _xlim=None):
        if not isinstance(data, physio.PeakFinder):
            raise TypeError('Input must be a sub-class of peakdet.PeakFinder')
        # save reference to data, time for plotting
        self.data = data
        self.time = np.arange(0, data.size / data.fs, 1. / data.fs)
        self.defxlim = _xlim
        self.plot = False
        # make main plot objects
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, tight_layout=True)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheel)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.span = SpanSelector(ax=self.ax, onselect=self.on_span, button=1,
                                 direction='horizontal', useblit=True,
                                 rectprops=dict(facecolor='red', alpha=0.3))
        self.plot_signals()

    def plot_signals(self):
        """ Clears axes and plots data / peaks / troughs """
        if self.plot:
            xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        else:
            self.plot = True
            xlim, ylim = (-5, self.defxlim), (None, None)

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

    def on_span(self, xmin, xmax):
        """ Manually removes physio peaks on span select """
        imin, imax = np.searchsorted(self.data.peaks,
                                     np.searchsorted(self.time, (xmin, xmax)))
        remove = np.arange(imin, imax, dtype=int)
        self.last_removed = self.data.peaks[remove]
        self.data._reject = np.append(self.data._reject,
                                      self.last_removed)
        self.data._find_troughs()
        self.plot_signals()

    def on_key(self, event):
        """ Undoes last span select or quits peak editor """
        if event.key == 'ctrl+z':
            self.undo()
        elif event.key == 'ctrl+q':
            self.quit()

    def undo(self):
        """ Resets last span select peak removal """
        if self.last_removed is None:
            return
        self.data._reject = np.setdiff1d(self.data._reject,
                                         self.last_removed)
        self.data._find_troughs()
        self.last_removed = None
        self.plot_signals()

    def quit(self):
        """ Closes peak editor """
        plt.close(self.fig)
