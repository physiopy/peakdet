#!/usr/bin/env python

import os
import Tkinter as Tk
import ttk
import warnings
import tkFileDialog
import tkMessageBox
import fnmatch
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector


class PeakDetector(object):
    """A GUI for use in detecting peaks in physiological signals"""

    def __init__(self, master):
        self.master = master
        self._init_main_frame()
        self._init_menu()

###############################################################################
#####################  UPDATING GUI DISPLAY FUNCTIONS    ######################
# This section of code is used for updating the GUI. Any additional functions #
# that alter visual aspects of the GUI should be added here.                  #
###############################################################################

    def _init_main_frame(self):
        """Generates main frame of GUI"""

        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=Tk.BOTH, expand=True)

        self.buttonFrame = ttk.Frame(self.frame)
        self.buttonFrame.pack(fill=Tk.BOTH, expand=1)

        self.welcomeText = ttk.Label(self.buttonFrame, text="Peak Detection GUI")
        self.welcomeText.pack(side=Tk.TOP, pady=10)

        self.quitbtn = ttk.Button(self.frame, text="QUIT", command=self._quit)
        self.quitbtn.pack(side=Tk.BOTTOM)
        self.quitbtn.bind('<Return>', self._quit)

        self.openbtn = ttk.Button(self.frame, text="OPEN FILE",command=self._get_file)
        self.openbtn.pack(side=Tk.BOTTOM)
        self.openbtn.bind('<Return>', self._get_file)

        self._plot_exists = False
        self._center_window(350,150)

    def _init_menu(self):
        """Generates menu bar"""
        menubar = Tk.Menu(self.master)
        self.master.config(menu=menubar)

        fileMenu = Tk.Menu(menubar,tearoff=False)
        fileMenu.add_command(label="Open", command=self._get_file, accelerator='Ctrl+O')
        fileMenu.add_command(label="Save", command=self._save_file, accelerator='Ctrl+S')
        fileMenu.add_command(label="Quit", command=self._quit, accelerator='Ctrl+Q')

        helpMenu = Tk.Menu(menubar,tearoff=False)
        helpMenu.add_command(label="Auto-save", command=self._autosave, accelerator='Ctrl+A')
        helpMenu.add_command(label="Warnings", command=self._warnings, accelerator='Ctrl+W')

        menubar.add_cascade(label="File", menu=fileMenu)
        menubar.add_cascade(label="Options", menu=helpMenu)

        self.master.bind_all("<Control-q>",self._quit)
        self.master.bind_all("<Control-o>",self._get_file)
        self.master.bind_all("<Control-s>",self._save_file)
        self.master.bind_all("<Control-a>",self._autosave)
        self.master.bind_all("<Control-n>",self._next_file)
        self.master.bind_all("<Control-b>",self._back_file)
        self.master.bind_all("<Control-w>",self._warnings)

    def _init_buttons(self):
        """Generates buttons to be used once file is loaded"""

        self.welcomeText.destroy()
        self.quitbtn.destroy()
        self.master.title("Peak detection and rejection")
        self._give_warnings = True
        self._auto_save = False

        # place frame containing buttons to right side of GUI
        self.buttonFrame.grid(row=0,column=3,
                              rowspan=5,columnspan=2,
                              padx=15,pady=10,
                              sticky=Tk.N+Tk.W+Tk.S+Tk.E)

        # radio buttons
        self.mode = Tk.IntVar(self.buttonFrame)
        self.mode.set(0)
        radiobuttons = ["No action", "Accept peaks", "Reject peaks",
                        "Multiple peak accept","Multiple peak reject",
                        "Delete peaks"]

        for x in range(len(radiobuttons)):
            if x not in [3,4]: comm = self._turn_select_off
            elif x == 3: comm = self._turn_select_on
            elif x == 4: comm = self._turn_reject_on
            button = ttk.Radiobutton(self.buttonFrame,text=radiobuttons[x],
                                     variable=self.mode,value=x,command=comm)
            button.grid(row=x,column=0,pady=4,sticky=Tk.W)

        # threshold/stdev labels
        self.threshlab = ttk.Label(self.frame, text="Change threshold",takefocus=False)
        self.threshlab.grid(row=6,column=3,pady=4,sticky=Tk.W)
        self.stdlab = ttk.Label(self.frame,text="Change SD",takefocus=False)
        self.stdlab.grid(row=7,column=3,pady=4,sticky=Tk.W)

        # change threshold spinbox
        self.threshold = Tk.StringVar(self.frame)
        self.threshold.set("0.95")
        self.threshbtn = Tk.Spinbox(self.frame,from_=0,to_=1.0,increment=0.01,
                                    width=4,exportselection=True,
                                    textvariable=self.threshold,
                                    command=self._set_thresh)
        self.threshbtn.grid(row=6, column=4, pady=4)
        self.threshbtn.bind('<Return>',self._set_thresh)
        self.threshbtn.bind('<KP_Enter>',self._set_thresh)

        # change sd spinbox
        self.std = Tk.StringVar(self.frame)
        self.std.set("2.5")
        self.stdbtn = Tk.Spinbox(self.frame,from_=0,to_=10.0,increment=0.1,
                                 width=4,exportselection=True,
                                 textvariable=self.std,command=self._set_std)
        self.stdbtn.grid(row=7, column=4, pady=4)
        self.stdbtn.bind('<Return>',self._set_std)
        self.stdbtn.bind('<KP_Enter>',self._set_std)

        labelframe = ttk.LabelFrame(self.frame, text='Notes')
        labelframe.grid(row=8,column=3,columnspan=2,sticky=Tk.N+Tk.W, pady=10)

        self.textwidg = Tk.Text(labelframe, width=24, takefocus=0)
        self.textwidg.grid(row=1,column=1,pady=4,padx=4)

        # for filename display
        self.fnamestr = Tk.StringVar(self.frame)
        fnamelab = ttk.Label(self.frame, textvariable=self.fnamestr, takefocus=0)
        fnamelab.grid(row=10,column=2,pady=4,sticky=Tk.E)

        # regrid open button
        self.openbtn.grid(row=9,column=3,pady=4)

        # save button
        self.savebtn = ttk.Button(self.frame, text = "SAVE", command=self._save_file)
        self.savebtn.bind('<Return>',self._save_file)
        self.savebtn.grid(row=9, column=4, pady=4)

        # next and back buttons
        self.backbtn = ttk.Button(self.frame, text = "BACK", command=self._back_file)
        self.nextbtn = ttk.Button(self.frame, text = "NEXT", command=self._next_file)
        self.backbtn.grid(row=10, column=3, pady=4)
        self.nextbtn.grid(row=10, column=4, pady=4)
        self.backbtn.bind('<Return>',self._back_file)
        self.nextbtn.bind('<Return>',self._next_file)

        create_tooltip(self.stdlab,"Set stdev cutoff")
        create_tooltip(self.threshlab,"Set % overlap")    

    def _center_window(self,w,h):
        """Centers window on screen"""

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2

        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def _init_plot(self):
        """Initializes plotting interface with original and filtered signals"""
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(8,weight=1)

        self.f = Figure(facecolor='#cccccc',edgecolor='#d6d6d6',tight_layout=True)

        self.ax0 = self.f.add_subplot(211)
        self.ax1 = self.f.add_subplot(212,sharex=self.ax0)

        self.canvas = FigureCanvasTkAgg(self.f, master=self.frame)
        self.canvas.get_tk_widget().grid(row=0, column=0,
                                         columnspan=3, rowspan=10,
                                         pady=5, padx=5,
                                         sticky=Tk.N+Tk.E+Tk.W+Tk.S)
        self.canvas.show()
        self.canvas.mpl_connect('pick_event',self._on_pick)
        self.canvas.mpl_connect('scroll_event',self._roll_wheel)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame)
        toolbar.grid(row=10,column=0,columnspan=2,sticky=Tk.N+Tk.E+Tk.W+Tk.S)
        toolbar.set_message = lambda x: ''
        toolbar.update()

        self.span = SpanSelector(self.ax1,self._on_span_select,'horizontal',
                                 minspan=1,useblit=True)
        self.span.visible = False

    def _plot_signals(self,newFile=False):
        """Plots signal and filtered signal with peaks"""

        if not self._plot_exists or newFile:
            self._plot_exists = True
            a0 = ((-50,None),(None,None))
            a1 = ((-50,None),(None,None))
        else:
            a0 = self.ax0.get_xlim(),self.ax0.get_ylim()
            a1 = self.ax1.get_xlim(),self.ax1.get_ylim()

        self.ax0.clear()
        self.ax1.clear()

        self.ax0.plot(self.time,self.orig_signal)
        self.ax0.set_xlim(a0[0][0],a0[0][1])
        self.ax0.set_ylim(a0[1][0],a0[1][1])
        self.ax0.set_yticklabels('')

        self.ax1.plot(self.time,self.signal)
        self.ax1.plot(self.time[self.keepPeaks],self.signal[self.keepPeaks],'g.',picker=6)
        self.ax1.plot(self.time[self.rejectPeaks],self.signal[self.rejectPeaks],'ro',picker=6)
        if self.ftype == 'Resp':
            self.ax1.plot(self.time[self.troughind],self.signal[self.troughind],'m.',picker=6)
        self.ax1.set_ylim(a1[1][0],a1[1][1])
        self.ax1.set_yticklabels('')

        self.canvas.draw()

###############################################################################
######################     MENU AND BUTTON FUNCTIONS      #####################
# This section of code should be used only for menu and button functions. If  #
# you are binding a command to any portion of the GUI, add the code for it    #
# here.                                                                       #
###############################################################################

    def _quit(self,event=None):
        """Exits application; bound to QUIT button"""

        if event:
            if event.widget != self.quitbtn and event.keycode != 24: return
        if tkMessageBox.askyesno("Quit GUI", message="Do you really want to quit?"):
            if self._plot_exists: self._comp_RRT_file()
            self.master.quit()
            self.master.destroy()

    def _autosave(self,event=None):
        if self._auto_save:
            self._auto_save = False
            print("Auto-save has been turned OFF")
        else:
            self._auto_save = True
            print("Auto-save has been turned ON")

    def _get_file(self,event=None):
        """Opens file dialog; bound to OPEN FILE button"""

        if event:
            if event.widget != self.openbtn and event.keycode != 32: return

        ftypes = [('AFNI', '*.1D'), ('CSV', '*.csv'), ('TXT','*.txt'), ('All files', '*')]
        dlg = tkFileDialog.Open(self.master, filetypes=ftypes)
        temp_fname = dlg.show()
        if temp_fname == () or temp_fname == '': return
        else:
            self.fname = temp_fname
            self._load_file()

    def _load_file(self):
        """Parses a file name"""
        if not self._plot_exists:
            self._init_buttons()
            self._init_plot()
            self._center_window(self.master.winfo_screenwidth(),
                                self.master.winfo_screenheight())

        if self.fname.find('ECG') != -1:
            self.ftype = 'ECG'
            if not len(self.stdbtn.grid_info()): self.stdbtn.grid()
            if not len(self.threshbtn.grid_info()): self.threshbtn.grid()
        elif self.fname.find('Resp') != -1:
            self.ftype = 'Resp'
            if len(self.stdbtn.grid_info()): self.stdbtn.grid_remove()
            if len(self.threshbtn.grid_info()): self.threshbtn.grid_remove()
        else:
            raise TypeError("File must have ECG or Resp in name.")

        # this is just for CMRIF physio files
        if self.fname.find('new.1D') != -1: self.fs = 1000.
        elif self.fname.find('scan_00') != -1: self.fs = 50.
        else: self.fs = 40.

        self.orig_signal = np.loadtxt(self.fname)
        self.time = np.arange(0,self.orig_signal.size/self.fs,1./self.fs)

        prefPath, actFile = os.path.split(self.fname)

        allFiles = os.listdir(prefPath)
        if '.notes' in allFiles: allFiles.remove('.notes')
        else: os.mkdir(os.path.join(prefPath,'.notes'))

        self._allFiles = [x for x in allFiles if x not in fnmatch.filter(allFiles,'RRT*')]
        self._allFiles.sort()

        self._find_peaks()

        if os.path.exists(prefPath+'/RRT_'+actFile) and os.path.exists(prefPath+'/RRT_reject_'+actFile):
            self.keepPeaks = np.loadtxt(prefPath+'/RRT_'+actFile,usecols=[0],dtype='int64')
            self.rejectPeaks = np.loadtxt(prefPath+'/RRT_reject_'+actFile,usecols=[0],dtype='int64')
            self.peakind = np.sort(np.append(self.keepPeaks,self.rejectPeaks))
            if self.ftype == 'Resp': self.troughind = np.loadtxt(prefPath+'/RRT_'+actFile,usecols=[1],dtype='int64')

        self.textwidg.delete("1.0",Tk.END)

        if os.path.exists(prefPath+'/.notes/notes_'+actFile):
            with open(prefPath+'/.notes/notes_'+actFile,'rb') as f:
                text = f.read()
            self.textwidg.insert(Tk.END,text)

        self.fnamestr.set('File: '+actFile)
        self._plot_signals(True)

    def _save_file(self,event=None):
        """Bound to SAVE PEAK button"""

        if event:
            if event.widget != self.savebtn and event.keycode != 39: return

        prefPath, actFile = os.path.split(self.fname)

        if not os.path.exists(prefPath+'/.notes'): os.mkdir(prefPath+'/.notes')

        if self.ftype == 'Resp':
            if self.troughind.size > self.keepPeaks.size: self.troughind = np.delete(self.troughind,0)
            elif self.keepPeaks.size > self.troughind.size: self.keepPeaks = np.delete(self.keepPeaks,0)
            to_save = np.hstack((self.keepPeaks.reshape(self.keepPeaks.size,1),
                                self.troughind.reshape(self.troughind.size,1)))
            np.savetxt('%s/RRT_%s'% (prefPath, actFile),to_save,fmt='%i %i')
        else:
            np.savetxt(prefPath+'/RRT_'+actFile,self.keepPeaks,fmt='%i')
        np.savetxt(prefPath+'/RRT_reject_'+actFile,self.rejectPeaks,fmt='%i')

        self._save_notes()

        print("Saved peak files for %s." % actFile)

    def _save_notes(self):
        prefPath, actFile = os.path.split(self.fname)

        temp = open(prefPath+'/.notes/notes_'+actFile,'w')
        temp.write(self.textwidg.get("1.0",'end-1c'))
        temp.close()

    def _set_thresh(self,event=None):
        """Bound to THRESHOLD SPINBOX"""

        if event:
            if event.widget != self.threshbtn: return

        self._get_above_thresh(thresh=float(self.threshold.get()))
        self._plot_signals()

    def _set_std(self,event=None):
        """Bound to STDEV SPINBOX"""

        if event:
            if event.widget != self.stdbtn: return

        self._goodInd = thresh_peaks(self._averageSig,sd=float(self.std.get()))
        self._get_above_thresh(thresh=float(self.threshold.get()))
        self._plot_signals()

    def _on_pick(self,event):
        """Bound to PLOT"""
        if self.mode.get() == 0 or event.mouseevent.button != 1:
            return

        thesedots = event.artist
        xdata = thesedots.get_xdata()
        ind = event.ind

        if self.ftype=='Resp':
            if xdata.size == self.troughind.size and np.allclose(xdata,self.time[self.troughind]):
                return

        if self.mode.get() == 1:  # accept
            if xdata.size == self.rejectPeaks.size and np.allclose(xdata,self.time[self.rejectPeaks]):
                self.keepPeaks = np.sort(np.append(self.keepPeaks,self.rejectPeaks[ind[0]]))
                self.rejectPeaks = np.delete(self.rejectPeaks,ind[0])

        elif self.mode.get() == 2:  # reject
            if xdata.size == self.keepPeaks.size and np.allclose(xdata,self.time[self.keepPeaks]):
                self.rejectPeaks = np.sort(np.append(self.rejectPeaks,self.keepPeaks[ind[0]]))
                self.keepPeaks = np.delete(self.keepPeaks,ind[0])

        elif self.mode.get() == 5:  # delete
            if tkMessageBox.askokcancel("Delete peak",
                                        "Do you really want to delete that peak? (Cannot be undone)"):
                if xdata.size == self.keepPeaks.size and np.allclose(xdata,self.time[self.keepPeaks]):
                    deleted_amp = self.keepPeaks[ind[0]]
                    self.keepPeaks = np.delete(self.keepPeaks,ind[0])
                elif xdata.size == self.rejectPeaks.size and np.allclose(xdata,self.time[self.rejectPeaks]):
                    deleted_amp = self.rejectPeaks[ind[0]]
                    self.rejectPeaks = np.delete(self.rejectPeaks,ind[0])

                new_peakind = np.sort(np.append(self.keepPeaks,self.rejectPeaks))
                deleted = np.setdiff1d(np.arange(self.peakind.size),np.searchsorted(self.peakind,new_peakind))
                self.peakind = new_peakind

                if self.ftype == 'ECG':
                    self._averageSig = np.delete(self._averageSig,deleted[0],0)
                    self._goodInd = thresh_peaks(self._averageSig,sd=float(self.std.get()))
                    self._get_above_thresh(thresh=float(self.threshold.get()))

                if self.ftype == 'Resp':
                    if self.peakind[0] < self.troughind[0]: 
                        bad_idx = deleted[0]-1+np.abs(self.signal[self.troughind[deleted[0]-1:deleted[0]+1]]-self.signal[deleted_amp]).argmin()
                    else:
                        bad_idx = deleted[0]+np.abs(self.signal[self.troughind[deleted[0]:deleted[0]+2]]-self.signal[deleted_amp]).argmin()
                    self.troughind = np.delete(self.troughind,bad_idx)

        self._plot_signals()

    def _on_span_select(self,xmin,xmax):
        """Bound to SPAN SELECTOR"""
        indmin, indmax = np.searchsorted(self.time, (xmin, xmax))

        if self.mode.get() == 3: #mult accept
            low, high = np.searchsorted(self.rejectPeaks, (indmin,indmax))
            self.keepPeaks = np.sort(np.append(self.keepPeaks,self.rejectPeaks[low:high]))
            self.rejectPeaks = np.delete(self.rejectPeaks,np.arange(low,high,dtype='int64'))

        elif self.mode.get() == 4: #mult reject
            low, high = np.searchsorted(self.keepPeaks, (indmin,indmax))
            self.rejectPeaks = np.sort(np.append(self.rejectPeaks,self.keepPeaks[low:high]))
            self.keepPeaks = np.delete(self.keepPeaks,np.arange(low,high,dtype='int64'))

        self._plot_signals()

    def _turn_select_on(self):
        """Bound to RADIOBUTTON MULTIPLE ACCEPT"""
        if not self.span.visible: self.span.visible = True

        if self.span.rectprops['facecolor'] != 'green':
            self.span.rectprops['facecolor'] = 'green'
            self.span.new_axes(self.span.ax)

    def _turn_reject_on(self):
        """Bound to RADIOBUTTON MULTIPLE REJECT"""
        if not self.span.visible: self.span.visible = True

        if self.span.rectprops['facecolor'] != 'red':
            self.span.rectprops['facecolor'] = 'red'
            self.span.new_axes(self.span.ax)

    def _turn_select_off(self):
        """Bound to RADIOBUTTONS 1, 2, and 3"""
        if self.span.visible: self.span.visible = False

    def _next_file(self,event=None):
        """Bound to NEXT button"""
        if event:
            if event.widget != self.nextbtn and event.keycode != 57: return

        if self._auto_save: self._save_file()
        else: self._comp_RRT_file()
        self._save_notes()

        prefPath, actFile = os.path.split(self.fname)
        ind = self._allFiles.index(actFile)

        if ind+1>=len(self._allFiles):
            if os.name == 'posix':
                print("\033[91mReached end of file list! Wrapping around to beginning...\033[0m")
            else:
                print("Reached end of file list! Wrapping around to beginning...")
            self.fname = prefPath+'/'+self._allFiles[0]
        else:
            self.fname = prefPath+'/'+self._allFiles[ind+1]

        self._load_file()

    def _back_file(self,event=None):
        """Bound to NEXT button"""
        if event:
            if event.widget != self.backbtn and event.keycode != 56: return

        if self._auto_save: self._save_file()
        else: self._comp_RRT_file()
        self._save_notes()

        prefPath, actFile = os.path.split(self.fname)
        ind = self._allFiles.index(actFile)

        if ind-1 == -1:
            if os.name == 'posix':
                print("\033[91mReached beginning of file list! Wrapping around to end...\033[0m")
            else:
                print("Reached beginning of file list! Wrapping around to end...")

        self.fname = prefPath+'/'+self._allFiles[ind-1]

        self._load_file()

    def _warnings(self,event=None):
        if self._give_warnings:
            self._give_warnings = False
            print("Warning have been turned OFF")
        else:
            self._give_warnings = True
            print("Warnings have been turned ON")

    def _comp_RRT_file(self, save=True):
        prefPath, actFile = os.path.split(self.fname)

        if os.path.exists(prefPath+'/RRT_'+actFile) and os.path.exists(prefPath+'/RRT_reject_'+actFile):
            compkeepPeaks = np.loadtxt(prefPath+'/RRT_'+actFile,usecols=[0],dtype='int64')
            comprejectPeaks = np.loadtxt(prefPath+'/RRT_reject_'+actFile,usecols=[0],dtype='int64')

            if (self.keepPeaks.size == compkeepPeaks.size and
                self.rejectPeaks.size == comprejectPeaks.size and
                np.allclose(self.keepPeaks,compkeepPeaks) and
                np.allclose(self.rejectPeaks,comprejectPeaks)):
                save = False

        if save and self._give_warnings:
            resp = tkMessageBox.askquestion("Save file",
                                            message="Peak file changes not saved! Do you want to save?",
                                            icon=tkMessageBox.WARNING)
            if resp == 'yes': self._save_file()

    def _roll_wheel(self, event):        
        if event.name != 'scroll_event':
            return

        a0 = self.ax0.get_xlim()
        self.ax0.set_xlim(a0[0]+(-10*event.step),a0[1]+(-10*event.step))
        self.canvas.draw()

###############################################################################
######################     PEAK DETECTION FUNCTIONS     #######################
# This section of code is used to detect peaks on the loaded signal data. All #
# functions relevant to processing of the signal should go here.              #
###############################################################################

    def _find_peaks(self):
        if self.ftype == 'ECG':
            # f_lims should be set based on normal frequencies for age group
            # lifespan cohorts should err conservative and take extremes
            f_lims, winsize  = np.array([0.5, 2.0]), int(0.25*self.fs)
            self._order = int(0.35*self.fs)
        elif self.ftype == 'Resp':
            winsize = int(1.0*self.fs)
            self._order = int(1.0*self.fs)

        # filter signal for better peak detection
        rasignal = run_avg_filt(self.orig_signal,winsize)

        if self.ftype == 'ECG':
            self.signal = bandpass_filt(rasignal,self.fs,f_lims)
            self._averageSig, self.peakind = avg_peak_wave(self.signal,self.fs,self._order)
            self._goodInd = thresh_peaks(self._averageSig)
            self.threshold.set("0.95")
        elif self.ftype == 'Resp':
            self.signal = rasignal.copy()
            # resp peak detection
            self._averageSig, self.peakind = avg_peak_wave(self.signal,self.fs,self._order)
            self.troughind = trough_det(self.signal,self.fs,self._order,self.peakind)
            self._goodInd = thresh_peaks(self._averageSig)
            self.threshold.set("0.00")

        self._get_above_thresh(thresh=float(self.threshold.get()))

    def _get_above_thresh(self, thresh=.95):
        self.keepPeaks = self.peakind[self._goodInd>=thresh]
        self.rejectPeaks = np.setdiff1d(self.peakind,self.keepPeaks)


###############################################################################
##########################     ASSIST FUNCTIONS       #########################
# This section of code should be used only for functions that assist the main #
# interface of the GUI, but do not need to be included in the class.          #
###############################################################################

class ToolTip(object):
    """For displaying tooltips associated with tkinter widgets"""

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = -10
        self.y = 10

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except Tk.TclError:
            pass
        label = Tk.Label(tw, text=self.text, justify=Tk.LEFT,
                         background="#ffffe0", relief=Tk.SOLID, borderwidth=1,
                         font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    """Creates tooltip associated with widget

    widget: object, tkinter widget
    text:   string, text to display upon hover
    """
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def extrap_signal(x_new, xp, yp):
    """Extrapolates signal (xp, yp) to x_new

    x:  array, desired x-values
    xp: array, current x-values
    yp: array, current y-values
    """

    # thanks to @sastanin on stack overflow
    y_new = np.interp(x_new, xp, yp)
    y_new[x_new < xp[0]] = yp[0] + (x_new[x_new<xp[0]]-xp[0]) * (yp[0]-yp[1]) / (xp[0]-xp[1])
    y_new[x_new > xp[-1]]= yp[-1] + (x_new[x_new>xp[-1]]-xp[-1]) * (yp[-1]-yp[-2]) / (xp[-1]-xp[-2])

    return y_new


def bandpass_filt(signal,fs,flims):
    """Runs bandpass filter and returns filtered signal

    signal: array-like, signal of interest
    fs:     float, sampling rate of signal (samples / unit time)
    flims:  list-of-two, limits of bandpass filter
    """

    nyq_freq = fs*0.5
    nyq_cutoff = np.array(flims)/nyq_freq
    b, a = scipy.signal.butter(3,nyq_cutoff,btype='bandpass')
    filtSig = scipy.signal.filtfilt(b,a,signal)

    return filtSig


def run_avg_filt(signal, winsize):
    """Runs running-average filter and returns filtered signal

    signal:  array-like, signal of interest
    winsize: int, window size for filter
    """

    filtSig = np.zeros(signal.size)
    bottom = lambda x: 0 if x < winsize else x

    halfWin = int(((winsize-winsize%2)/2)+1)

    for x in np.arange(signal.size):
        filtSig[x] = np.mean(signal[bottom(x-halfWin+winsize%2):x+halfWin])

    return filtSig


def avg_peak_wave(signal, fs, order):
    """Returns an array of waveforms around peaks in signal and indices of peaks

    signal:  array-like, signal of interest
    fs:      float, sampling rate of signal (samples / unit time)
    order:   int, number of datapoints to determine peaks
    extrema: int, 1 = peaks, 2 = troughs
    """

    peakind = (scipy.signal.argrelmax(signal,order=order))[0]
    rrAvg = int(np.mean(peakind[1:peakind.size]-peakind[0:peakind.size-1])/2)
    averageSig = np.zeros((peakind.size,rrAvg*2))
    time = np.arange(0,signal.size/float(fs),1./fs)

    bottomOut = lambda x: 0 if x<0 else x
    topOut = lambda x: -1 if x>signal.size else x

    for x in np.arange(peakind.size):
        high = topOut(peakind[x]+rrAvg)
        low = bottomOut(peakind[x]-rrAvg)

        tempSig = signal[low:high]

        if tempSig.size != rrAvg*2 and low == 0:
            x_new = np.arange(time[high]-(rrAvg*2.*(1./fs)),
                              time[high],
                              1./fs)[0:rrAvg*2]
            tempSig = extrap_signal(x_new,time[low:high],signal[low:high])

        elif tempSig.size != rrAvg*2 and high == -1:
            x_new = np.arange(time[low],
                              time[low]+(rrAvg*2.*(1./fs)),
                              1./fs)[0:rrAvg*2]
            tempSig = extrap_signal(x_new,time[low:high],signal[low:high])

        averageSig[x] = tempSig

    return averageSig, peakind


def trough_det(signal, fs, order, peakind):
    """Returns indices of troughs in signal, with only one b/w each peak in peakind

    signal:  array-like, signal of interest
    fs:      float, sampling rate of signal (samples / unit time)
    order:   int, number of datapoints to determine peaks
    peakind: array-like, indices of probabilistic peaks
    """

    troughind = (scipy.signal.argrelmin(signal,order=order))[0]

    for peak in np.arange(1,peakind.size):
        troughs = troughind[np.logical_and(troughind>peakind[peak-1],troughind<=peakind[peak])]
        if troughs.size == 0:
            snippet = signal[peakind[peak-1]:peakind[peak]]
            troughs = np.where(snippet == snippet.min()) + peakind[peak-1]
            troughind = np.append(troughind,troughs[0])
            troughind.sort()
        elif troughs.size > 1:
            trough_amp = signal[troughs]
            bad_troughs = troughs[np.where(trough_amp != trough_amp.min())[0]]
            for t in bad_troughs: troughind = np.delete(troughind,np.where(troughind==t)[0])

    troughs = troughind[troughind>peakind[-1]]
    if troughs.size > 1:
        trough_amp = signal[troughs]
        bad_troughs = troughs[np.where(trough_amp != trough_amp.min())[0]]
        for t in bad_troughs: troughind = np.delete(troughind,np.where(troughind==t)[0])

    troughs = troughind[troughind<peakind[0]]
    if troughs.size > 1:
        trough_amp = signal[troughs]
        bad_troughs = troughs[np.where(trough_amp != trough_amp.min())[0]]
        for t in bad_troughs: troughind = np.delete(troughind,np.where(troughind==t)[0])

    return troughind


def thresh_peaks(averageSig,sd=2.5):
    """Returns % overlap of each row of averageSig with mean(averageSig)+-sd

    averageSig: array, waveforms of probable peaks
    sd:         float, stdevs away from mean waveform to consider peak waveforms
    """
    meanSig = np.mean(averageSig,0)
    ci = sd*np.std(averageSig,0)

    low = meanSig-ci
    high = meanSig+ci

    goodInd = []

    for samp in np.arange(averageSig.shape[0]):
        currSigWin = averageSig[samp]
        logInd = np.logical_and(currSigWin >= low, currSigWin <= high)
        numOverlap = float(logInd[logInd].size)
        percOverlap = numOverlap/averageSig.shape[1]

        goodInd.append(round(percOverlap,3))

    return np.array(goodInd)


if __name__ == '__main__':
    warnings.filterwarnings('ignore',r'loadtxt: Empty input file: ')

    root = Tk.Tk()
    app = PeakDetector(root)
    root.title("")
    root.update()
    root.mainloop()