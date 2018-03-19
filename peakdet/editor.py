# -*- coding: utf-8 -*-

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk
import numpy as np
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
import peakdet


class PeakEditor(object):
    """
    Class for editing detected peaks
    """

    def __init__(self, input, _debug=False, _xlim=None):

        if not isinstance(input, peakdet.PeakFinder):
            raise TypeError("Input must be a sub-class of peakdet.PeakFinder")
        self.peakfinder = input
        self.defxlim = _xlim
        self.master = tk.Tk()
        self.master.title("Interactive peak editor")
        self.master.bind_all("<Control-q>", self.done)
        self.master.bind_all("<Control-z>", self.undo)
        self.master.geometry('%dx%d+%d+%d' % (self.master.winfo_screenwidth(),
                                              self.master.winfo_screenheight(),
                                              0, 0))
        self.create_main()
        self.master.update()
        if not _debug:
            self.master.mainloop()

    def create_main(self):
        frame = ttk.Frame(self.master)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(8, weight=1)

        f = Figure(facecolor='#cccccc', edgecolor='#d6d6d6', tight_layout=True)
        ax, self.plot = f.add_subplot(111), False

        canvas = FigureCanvasTkAgg(f, master=frame)
        canvas.get_tk_widget().grid(row=0, column=0,
                                    rowspan=10, columnspan=3,
                                    pady=5, padx=5,
                                    sticky=tk.N + tk.W + tk.S + tk.E)
        canvas.mpl_connect('scroll_event', self.roll_wheel)
        canvas.draw()

        span = SpanSelector(ax=ax,
                            onselect=self.on_span_select,
                            direction='horizontal',
                            useblit=True,
                            button=1)
        span.rectprops['facecolor'] = 'red'
        span.new_axes(span.ax)

        self.ax, self.canvas, self.span = ax, canvas, span
        self.plot_signals()

    def plot_signals(self):
        if self.plot:
            lim = self.ax.get_xlim(), self.ax.get_ylim()
        else:
            self.plot, lim = True, ((-5, self.defxlim), (None, None))

        self.ax.clear()
        self.ax.plot(self.peakfinder.time,
                     self.peakfinder.data, 'b',
                     self.peakfinder.time[self.peakfinder.peakinds],
                     self.peakfinder.data[self.peakfinder.peakinds], '.r',
                     self.peakfinder.time[self.peakfinder.troughinds],
                     self.peakfinder.data[self.peakfinder.troughinds], '.g')
        self.ax.set(xlim=lim[0], ylim=lim[1], yticklabels='')

        self.canvas.draw()

    def roll_wheel(self, event):
        lim, move = self.ax.get_xlim(), event.step * -10
        self.ax.set_xlim(lim[0] + move, lim[1] + move)
        self.canvas.draw()

    def on_span_select(self, xmin, xmax):
        imin, imax = np.searchsorted(self.peakfinder.time, (xmin, xmax))
        imin, imax = np.searchsorted(self.peakfinder.peakinds, (imin, imax))
        remove = np.arange(imin, imax, dtype='int')

        self.last_removed = self.peakfinder.peakinds[remove]
        self.peakfinder._rejected = np.append(self.peakfinder._rejected,
                                              self.last_removed)

        self.peakfinder.get_troughs(thresh=0)
        self.plot_signals()

    def undo(self, event=None):
        if self.last_removed is not None:
            self.peakfinder._rejected = np.setdiff1d(self.peakfinder._rejected,
                                                     self.last_removed)
            # self.peakfinder._peakinds = np.append(self.peakfinder.peakinds,
            #                                       self.last_removed)
            # self.peakfinder._peakinds.sort()
            self.peakfinder.get_troughs(thresh=0)
            self.last_removed = None
            self.plot_signals()

    def done(self, event=None):
        self.master.quit()
        self.master.destroy()
