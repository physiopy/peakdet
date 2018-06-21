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
        self.defxlim = _xlim
        self.plot = False
        self.create_main()
        self.plot_signals()

    def create_main(self):
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1,
                                         facecolor='#cccccc',
                                         edgecolor='#d6d6d6',
                                         tight_layout=True)
        self.fig.canvas.mpl_connect('scroll_event', self.on_roll)
        self.fig.canvas.mpl_connect('on_key', self.on_key)
        self.span = SpanSelector(ax=self.ax,
                                 onselect=self.on_span,
                                 direction='horizontal',
                                 useblit=True,
                                 button=1,
                                 rectprops=dict(facecolor='red'))

    def plot_signals(self):
        if self.plot:
            xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        else:
            self.plot = True
            xlim, ylim = (-5, self.defxlim), (None, None)

        self.ax.clear()
        self.ax.plot(self.time,
                     self.data, 'b',
                     self.time[self.data.peakinds],
                     self.data[self.data.peakinds], '.r',
                     self.time[self.data.troughinds],
                     self.data[self.data.troughinds], '.g')
        self.ax.set(xlim=xlim, ylim=ylim, yticklabels='')
        self.fig.canvas.draw()

    def on_wheel(self, event):
        lim, move = self.ax.get_xlim(), event.step * -10
        self.ax.set_xlim(lim[0] + move, lim[1] + move)
        self.fig.canvas.draw()

    def on_span(self, xmin, xmax):
        imin, imax = np.searchsorted(self.time, (xmin, xmax))
        imin, imax = np.searchsorted(self.data.peakinds, (imin, imax))
        remove = np.arange(imin, imax, dtype=int)

        self.last_removed = self.data.peakinds[remove]
        self.data._rejected = np.append(self.data._rejected,
                                        self.last_removed)

        self.data.get_troughs(thresh=0)
        self.plot_signals()

    def on_key(self, event):
        if event.key == 'ctrl+u':
            self.undo()
        elif event.key == 'ctrl+q':
            self.quit()

    def undo(self):
        if self.last_removed is None:
            return
        self.data._rejected = np.setdiff1d(self.data._rejected,
                                           self.last_removed)
        self.data.get_troughs(thresh=0)
        self.last_removed = None
        self.plot_signals()

    def quit(self):
        plt.close(self.fig)
