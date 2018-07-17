# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from peakdet import physio


class PeakEditor():
    """
    Class for editing detected peaks
    """

    def __init__(self, data, _debug=False, _xlim=None):
        if not isinstance(data, physio.PeakFinder):
            raise TypeError('Input must be a sub-class of peakdet.PeakFinder')
        self.data = data
        self.time = np.arange(0, data.size / data.fs, 1. / data.fs)
        self.defxlim = _xlim
        self.plot = False
        self.create_main()
        self.plot_signals()

    def create_main(self):
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1,
                                         facecolor='#cccccc',
                                         edgecolor='#d6d6d6',
                                         tight_layout=True)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheel)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.span = SpanSelector(ax=self.ax,
                                 onselect=self.on_span,
                                 direction='horizontal',
                                 useblit=True,
                                 button=1,
                                 rectprops=dict(facecolor='red', alpha=0.3))

    def plot_signals(self):
        if self.plot:
            xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        else:
            self.plot = True
            xlim, ylim = (-5, self.defxlim), (None, None)

        self.ax.clear()
        self.ax.plot(self.time,
                     self.data, 'b',
                     self.time[self.data.peaks],
                     self.data[self.data.peaks], '.r',
                     self.time[self.data.troughs],
                     self.data[self.data.troughs], '.g')
        self.ax.set(xlim=xlim, ylim=ylim, yticklabels='')
        self.fig.canvas.draw()

    def on_wheel(self, event):
        lim, move = self.ax.get_xlim(), event.step * -10
        self.ax.set_xlim(lim[0] + move, lim[1] + move)
        self.fig.canvas.draw()

    def on_span(self, xmin, xmax):
        imin, imax = np.searchsorted(self.time, (xmin, xmax))
        imin, imax = np.searchsorted(self.data.peaks, (imin, imax))
        remove = np.arange(imin, imax, dtype=int)

        self.last_removed = self.data.peaks[remove]
        self.data._reject = np.append(self.data._reject,
                                      self.last_removed)

        self.data._find_troughs()
        self.plot_signals()

    def on_key(self, event):
        if event.key == 'ctrl+u':
            self.undo()
        elif event.key == 'ctrl+q':
            self.quit()

    def undo(self):
        if self.last_removed is None:
            return
        self.data._reject = np.setdiff1d(self.data._reject,
                                         self.last_removed)
        self.data._find_troughs()
        self.last_removed = None
        self.plot_signals()

    def quit(self):
        plt.close(self.fig)
