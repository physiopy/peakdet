# -*- coding: utf-8 -*-
"""
Functions for processing and interpreting physiological data
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate, signal
from peakdet import editor, utils


@utils.make_operation()
def filter_physio(data, cutoffs, method, *, order=3):
    """
    Applies an `order`-order digital `method` Butterworth filter to `data`

    Parameters
    ----------
    data : Physio_like
        Input physiological data to be filtered
    cutoffs : int or list
        If `method` is 'lowpass' or 'highpass', an integer specifying the lower
        or upper bound of the filter (in Hz). If method is 'bandpass' or
        'bandstop', a list specifying the lower and upper bound of the filter
        (in Hz).
    method : {'lowpass', 'highpass', 'bandpass', 'bandstop'}
        The type of filter to apply to `data`
    order : int, optional
        Order of filter to be applied. Default: 3

    Returns
    -------
    filtered : :class:`peakdet.Physio`
        Filtered input `data`
    """

    _valid_methods = ['lowpass', 'highpass', 'bandpass', 'bandstop']

    data = utils.check_physio(data, ensure_fs=True)
    if method not in _valid_methods:
        raise ValueError('Provided method {} is not permitted; must be in {}.'
                         .format(method, _valid_methods))
    cutoffs = np.array(cutoffs)
    if method in ['lowpass', 'highpass'] and cutoffs.size != 1:
        raise ValueError('Cutoffs must be length 1 when using {} filter'
                         .format(method))
    elif method in ['bandpass', 'bandstop'] and cutoffs.size != 2:
        raise ValueError('Cutoffs must be length 2 when using {} filter'
                         .format(method))

    nyq_cutoff = cutoffs / (data.fs * 0.5)
    if np.any(nyq_cutoff > 1):
        raise ValueError('Provided cutoffs {} are outside of the Nyquist '
                         'frequency for input data with sampling rate {}.'
                         .format(cutoffs, data.fs))

    b, a = signal.butter(int(order), nyq_cutoff, btype=method)
    filtered = utils.new_physio_like(data, signal.filtfilt(b, a, data))

    return filtered


@utils.make_operation()
def interpolate_physio(data, target_fs, *, kind='cubic'):
    """
    Interpolates `data` to desired sampling rate `target_fs`

    Parameters
    ----------
    data : Physio_like
        Input physiological data to be interpolated
    target_fs : float
        Desired sampling rate for `data`
    kind : str or int, optional
        Type of interpolation to perform. Must be one of available kinds in
        :func:`scipy.interpolate.interp1d`. Default: 'cubic'

    Returns
    -------
    interp : :class:`peakdet.Physio`
        Interpolated input `data`
    """

    data = utils.check_physio(data, ensure_fs=True)

    factor = target_fs / data.fs

    # generate original and target "time" series
    t_orig = np.linspace(0, len(data) / data.fs, len(data))
    t_new = np.linspace(0, len(data) / data.fs, int(len(data) * factor))

    # interpolate data and generate new Physio object
    interp = interpolate.interp1d(t_orig, data, kind=kind)(t_new)
    if data.suppdata is None:
        suppinterp = None
    else:
        suppinterp = interpolate.interp1d(t_orig, data.suppdata, kind=kind)(t_new)
    interp = utils.new_physio_like(data, interp, fs=target_fs, suppdata=suppinterp)

    return interp


@utils.make_operation()
def peakfind_physio(data, *, thresh=0.2, dist=None):
    """
    Performs peak and trough detection on `data`

    Parameters
    ----------
    data : Physio_like
        Input data in which to find peaks
    thresh : float [0,1], optional
        Relative height threshold a data point must surpass to be classified as
        a peak. Default: 0.2
    dist : int, optional
        Distance in indices that peaks must be separated by in `data`. If None,
        this is estimated. Default: None

    Returns
    -------
    peaks : :class:`peakdet.Physio`
        Input `data` with detected peaks and troughs
    """

    ensure_fs = True if dist is None else False
    data = utils.check_physio(data, ensure_fs=ensure_fs, copy=True)

    # first pass peak detection to get approximate distance between peaks
    cdist = data.fs // 4 if dist is None else dist
    thresh = np.squeeze(np.diff(np.percentile(data, [5, 95]))) * thresh
    locs, heights = signal.find_peaks(data[:], distance=cdist, height=thresh)

    # second, more thorough peak detection
    cdist = np.diff(locs).mean() // 2
    heights = np.percentile(heights['peak_heights'], 1)
    locs, heights = signal.find_peaks(data[:], distance=cdist, height=heights)
    data._metadata['peaks'] = locs
    # perform trough detection based on detected peaks
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks)

    return data


@utils.make_operation()
def delete_peaks(data, remove):
    """
    Deletes peaks in `remove` from peaks stored in `data`

    Parameters
    ----------
    data : Physio_like
    remove : array_like

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=True)
    data._metadata['peaks'] = np.setdiff1d(data._metadata['peaks'], remove)
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks, data.troughs)

    return data


@utils.make_operation()
def reject_peaks(data, remove):
    """
    Marks peaks in `remove` as rejected artifacts in `data`

    Parameters
    ----------
    data : Physio_like
    remove : array_like

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=True)
    data._metadata['reject'] = np.append(data._metadata['reject'], remove)
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks, data.troughs)

    return data


@utils.make_operation()
def add_peaks(data, add):
    """
    Add `newpeak` to add them in `data`

    Parameters
    ----------
    data : Physio_like
    add : int

    Returns
    -------
    data : Physio_like
    """

    data = utils.check_physio(data, ensure_fs=False, copy=True)
    idx = np.searchsorted(data._metadata['peaks'], add)
    data._metadata['peaks'] = np.insert(data._metadata['peaks'], idx, add)
    data._metadata['troughs'] = utils.check_troughs(data, data.peaks)

    return data


def edit_physio(data):
    """
    Opens interactive plot with `data` to permit manual editing of time series

    Parameters
    ----------
    data : Physio_like
        Physiological data to be edited

    Returns
    -------
    edited : :class:`peakdet.Physio`
        Input `data` with manual edits
    """

    data = utils.check_physio(data, ensure_fs=True)

    # no point in manual edits if peaks/troughs aren't defined
    if not (len(data.peaks) and len(data.troughs)):
        print(data.peaks, data.troughs)
        return

    # perform manual editing
    edits = editor._PhysioEditor(data)
    plt.show(block=True)

    # replay editing on original provided data object
    if len(edits.rejected) > 0:
        data = reject_peaks(data, remove=sorted(edits.rejected))
    if len(edits.deleted) > 0:
        data = delete_peaks(data, remove=sorted(edits.deleted))
    if len(edits.included) > 0:
        data = add_peaks(data, add=sorted(edits.included))

    return data


def plot_physio(data, *, ax=None):
    """
    Plots `data` and associated peaks / troughs

    Parameters
    ----------
    data : Physio_like
        Physiological data to plot
    ax : :class:`matplotlib.axes.Axes`, optional
        Axis on which to plot `data`. If None, a new axis is created. Default:
        None

    Returns
    -------
    ax : :class:`matplotlib.axes.Axes`
        Axis with plotted `data`
    """

    # generate x-axis time series
    fs = 1 if np.isnan(data.fs) else data.fs
    time = np.arange(0, len(data) / fs, 1 / fs)
    if ax is None:
        fig, ax = plt.subplots(1, 1)
    # plot data with peaks + troughs, as appropriate
    ax.plot(time, data, 'b',
            time[data.peaks], data[data.peaks], '.r',
            time[data.troughs], data[data.troughs], '.g')

    return ax


@utils.make_operation()
def neurokit_processing(data, modality, method, **kwargs):
    """
    Applies an `order`-order digital `method` Butterworth filter to `data`

    Parameters
    ----------
    data : Physio_like
        Input physiological data to be filtered
    modality : str
        Modality of the data.
        One of 'ECG', 'PPG', 'RSP', 'EDA',
    method : str
        The processing pipeline to apply, choose from neurokit2 lists

    Returns
    -------
    clean : :class:`peakdet.Physio`
        Filtered input `data`
    """
    try:
        import neurokit2 as nk
    except ImportError:
        raise ImportError('neurokit2 is required to use this function')
    modality = modality.upper()
    if modality not in ['ECG', 'PPG', 'RSP', 'EDA']:
        raise ValueError('Provided modality {} is not permitted; must be in {}.'
                         .format(modality, ['ECG', 'PPG', 'RSP', 'EDA']))

    data = utils.check_physio(data, ensure_fs=True)
    if modality == 'ECG':
        data = fmri_ecg_clean(data, method=method, **kwargs)
        signal, info = nk.ecg_peaks(data, method=method)
        info[f'{modality}_Peaks'] = info['ECG_R_Peaks']
    elif modality == 'PPG':
        signal, info = nk.ppg_process(data, sampling_rate=data.fs, method=method)
    elif modality == 'RSP':
        signal, info = nk.rsp_process(data, sampling_rate=data.fs, method=method)
    elif modality == 'EDA':
        signal, info = nk.eda_process(data, sampling_rate=data.fs, method=method)
        info[f'{modality}_Peaks'] = info['SCR_Peaks']
    data._metadata['peaks'] = np.array(info[f'{modality}_Peaks'])
    try:
        info[f'{modality}_Troughs']
        data._metadata['troughs'] = np.array(info[f'{modality}_Troughs'])
        data._metadata['troughs'] = utils.check_troughs(data, data.peaks, data.troughs)
    except KeyError:
        pass
    data._features['info'] = info
    data._features['signal'] = signal
    clean = utils.new_physio_like(data, signal[f'{modality}_Clean'].values)
    # ADD IN OTHER INFO as features
    return clean

# ======================================================================
# Electrocardiogram (ECG)
# =======================================================================


@utils.make_operation()
def fmri_ecg_clean(data, method="biopac", me=False, **kwargs):
    """
    Clean an ECG signal.

    Prepare a raw ECG signal for R-peak detection with the specified method.

    Parameters
    ----------
    data : Physio_like
        The raw ECG signal to clean.
    sampling_rate : float
        The sampling frequency of `ecg_signal` (in Hz, i.e., samples/second).
        Default to 10000.
    method : str
        The processing pipeline to apply between 'biopac' and 'bottenhorn'.
        Default to 'biopac'.
    me : bool
        Specify if the MRI sequence used was the multi-echo (True)
        or the single-echo (False).
        Default to False.
    downsampling : int
        The desired sampling frequency (Hz). If None, the signal is not resample.
        Default to None.

    Returns
    -------
    ecg_clean : :class:`peakdet.Physio`
        The cleaned ECG signal in object.
    """
    # check if the TR is specified
    if "tr" not in kwargs.keys():
        raise ValueError(
            "The TR must be specified when using the multi-echo sequence."
        )
    tr = kwargs["tr"]
    # check if the MB factor is specified
    if "mb" not in kwargs.keys():
        raise ValueError(
            "The multiband factor must be specified when using the multi-echo sequence."
        )
    mb = kwargs["mb"]
    # check if the number of slices is specified
    if "slices" not in kwargs.keys():
        raise ValueError(
            "The number of slices must be specified when using the multi-echo sequence."
        )
    slices = kwargs["slices"]

    if method in ["biopac"]:
        data = _ecg_clean_biopac(data, tr=tr, slices=slices)
    elif method in ["bottenhorn", "bottenhorn2022"]:
        # Apply comb band pass filter with Bottenhorn correction
        print("... Applying the corrected comb band pass filter.")
        ecg_clean = _ecg_clean_bottenhorn(data, tr=tr, mb=mb, slices=slices)
    else:
        raise ValueError(
            "The specified method is not supported. "
            "Please choose between 'biopac' and 'bottenhorn'."
        )

    return ecg_clean


# =============================================================================
# ECG internal : biopac recommendations
# =============================================================================
def _ecg_clean_biopac(data, tr=1.49, slices=60, Q=100):
    """
    Single-band sequence gradient noise reduction.

    This function is a reverse-engineered appropriation of BIOPAC's application note 242.
    It only applies to signals polluted by single-band (f)MRI sequence.

    Parameters
    ----------
    data : Physio_like
        The ECG signal in object.
    sampling_rate: float
        The sampling frequency of `ecg_signal` (in Hz, i.e., samples/second).
        Default to 10000.
    tr : int
        The time Repetition of the MRI scanner.
        Default to 1.49.
    slices :
        The number of volumes acquired in the tr period.
        Default to 60.
    Q : int
        The filter quality factor.
        Default to 100.

    Returns
    -------
    ecg_clean : array
        The cleaned ECG signal.

    References
    ----------
    Biopac Systems, Inc. Application Notes: application note 242
        ECG Signal Processing During fMRI
        https://www.biopac.com/wp-content/uploads/app242x.pdf
    """
    # Setting scanner sequence parameters
    nyquist = np.float64(data.fs / 2)
    notches = {"slices": slices / tr, "tr": 1 / tr}
    # remove baseline wandering
    data = filter_physio(
        data,
        cutoffs=2,
        method="highpass",
    )
    # Filtering at specific harmonics
    data = _comb_band_stop(notches, nyquist, data, Q)
    # bandpass filtering
    data_clean = filter_physio(
        data,
        cutoffs=[2, 20],
        method="bandpass",
        order=5,
    )

    return data_clean


def _ecg_clean_bottenhorn(
    data, tr=1.49, mb=4, slices=60, Q=100
):
    """
    Multiband sequence gradient noise reduction.

    Parameters
    ----------
    ecg_signal : array
        The ECG channel.
    sampling_rate : float
        The sampling frequency of `ecg_signal` (in Hz, i.e., samples/second).
        Default to 10000.
    tr : float
        The time Repetition of the MRI scanner.
        Default to 1.49.
    mb : 4
        The multiband acceleration factor.
        Default to 4.
    slices : int
        The number of volumes acquired in the tr period.
        Default to 60.
    Q : int
        The filter quality factor.
        Default to 100.

    Returns
    -------
    ecg_clean : array
        The cleaned ECG signal.

    References
    ----------
    Bottenhorn, K. L., Salo, T., Riedel, M. C., Sutherland, M. T., Robinson, J. L.,
        Musser, E. D., & Laird, A. R. (2021). Denoising physiological data collected
        during multi-band, multi-echo EPI sequences. bioRxiv, 2021-04.
        https://doi.org/10.1101/2021.04.01.437293

    See also
    --------
    https://neuropsychology.github.io/NeuroKit/_modules/neurokit2/signal/signal_filter.html#signal_filter
    """
    # Setting scanner sequence parameters
    nyquist = np.float64(data.fs / 2)
    notches = {"slices": slices / mb / tr, "tr": 1 / tr}

    # Remove low frequency artefacts: respiration & baseline wander using
    # high pass butterworth filter (order=2)
    print("... Applying high pass filter.")
    ecg_clean = filter_physio(
        data, cutoffs=2, method="highpass"
    )
    # Filtering at fundamental and specific harmonics per Biopac application note #265
    print("... Applying notch filter.")
    ecg_clean = _comb_band_stop(notches, nyquist, ecg_clean, Q)
    # Low pass filtering at 40Hz per Biopac application note #242
    print("... Applying low pass filtering.")
    ecg_clean = filter_physio(data, cutoffs=40, method="lowpass")
    # bandpass filtering
    ecg_clean = filter_physio(
        data,
        cutoffs=[2, 20],
        method="bandpass",
        order=5,
    )

    return ecg_clean


@utils.make_operation()
def _comb_band_stop(notches, nyquist, data, Q):
    """
    A serie of notch filters aligned with the scanner gradient's harmonics.

    Parameters
    ----------
    notches : dict
        Frequencies to use in the IIR notch filter.
    nyquist : float
        The Nyquist frequency.
    data : Physio_like
        Data to be filtered.
    Q : int
        The filter quality factor.

    Returns
    -------
    filtered : Physio_like
        The filtered signal.

    References
    ----------
    Biopac Systems, Inc. Application Notes: application note 242
        ECG Signal Processing During fMRI
        https://www.biopac.com/wp-content/uploads/app242x.pdf

    See also
    --------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.iirnotch.html
    """
    # band stoping each frequency specified with notches dict
    for notch in notches:
        for i in np.arange(1, int(nyquist / notches[notch])):
            f0 = notches[notch] * i
            w0 = f0 / nyquist
            b, a = signal.iirnotch(w0, Q)
            filtered = utils.new_physio_like(data, signal.filtfilt(b, a, data))

    return filtered
