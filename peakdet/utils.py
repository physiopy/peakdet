#!/usr/bin/env python

import numpy as np
from scipy.signal import butter, filtfilt, gaussian


def gen_flims(signal, fs):
    """
    Generates a 'best guess' of ideal frequency cutoffs for a bp filter

    Parameters
    ----------
    signal : array-like
    fs : float

    Returns
    -------
    list-of-two : optimal frequency cutoffs
    """

    signal = np.squeeze(signal)
    inds = peakfinder(signal,dist=int(fs/4))
    inds = peakfinder(signal,dist=np.ceil(np.diff(inds).mean())/2)
    freq = np.diff(inds).mean()/fs  # frequency of detected peaks

    return np.asarray([freq/2,freq*2])


def bandpass_filt(signal, fs, flims=None, btype='bandpass'):
    """
    Runs `btype` filter on `signal` of sampling rate `fs`

    Parameters
    ----------
    signal : array-like
    fs : float
    flims : array-like
        Bounds of filter
    btype : str
        Type of filter; one of ['band','low','high']

    Returns
    -------
    array : filtered signal
    """

    signal = np.squeeze(signal)
    if flims is None: flims = [0,fs]

    nyq_freq = fs*0.5
    nyq_cutoff = np.asarray(flims)/nyq_freq
    b, a = butter(3, nyq_cutoff, btype=btype)
    fsig = filtfilt(b, a, signal)

    return fsig


def normalize(data):
    """
    Normalizes `data` (subtracts mean and divides by std)

    Parameters
    ----------
    data : array-like

    Returns
    -------
    array: normalized data
    """

    if data.ndim > 1: raise IndexError("Input must be one-dimensional.")
    return (data - data.mean()) / data.std()


def get_extrema(data, peaks=True, thresh=0.4):
    """
    Find extrema in `data` by changes in sign of first derivative

    Parameters
    ----------
    data : array-like
    peaks : bool
        Whether to look for peaks (True) or troughs (False)
    thresh : float (0,1)

    Returns
    -------
    array : indices of extrema from `data`
    """

    if thresh < 0 or thresh > 1: raise ValueError("Thresh must be in (0,1).")

    if peaks: Indx = np.where(data > data.max()*thresh)[0]
    else: Indx = np.where(data < data.min()*thresh)[0]

    trend = np.sign(np.diff(data))
    idx = np.where(trend==0)[0]

    # get only peaks, and fix flat peaks
    for i in range(idx.size-1,-1,-1):
        if trend[min(idx[i]+1,trend.size)-1]>=0: trend[idx[i]] = 1
        else: trend[idx[i]] = -1

    if peaks: idx = np.where(np.diff(trend)==-2)[0]+1
    else: idx = np.where(np.diff(trend)==2)[0]+1

    return np.intersect1d(Indx,idx)


def min_peak_dist(locs, data, peaks=True, dist=250):
    """
    Ensures extrema `locs` in `data` are separated by at least `dist`

    Parameters
    ----------
    locs : array-like
        Extrema, typically from get_extrema()
    data : array-like
    peaks : bool
        Whether to look for peaks (True) or troughs (False)
    dist : int
        Minimum required distance (in datapoints) b/w `locs`

    Returns
    -------
    array : extrema separated by at least `dist`
    """

    if peaks: idx = data[locs].argsort()[::-1][:]
    else: idx = data[locs].argsort()[:]
    locs = locs[idx]
    idelete = np.ones(locs.size)<0

    for i in range(locs.size):
        if not idelete[i]:
            dist_diff = np.logical_and(locs>=locs[i]-dist, locs<=locs[i]+dist)
            idelete = np.logical_or(idelete, dist_diff)
            idelete[i] = 0

    return locs[~idelete]


def peakfinder(data, thresh=0.4, dist=250):
    """
    Finds peaks in `data`

    Parameters
    ----------
    data : array-like
    thresh : float (0,1)
    dist : int
        Minimum required distance (in datapoints) b/w peaks

    Returns
    -------
    array : peak locations (indices)
    """

    locs = get_extrema(data,thresh=thresh)
    locs = min_peak_dist(locs,data,dist=dist)

    return np.array(sorted(locs))


def troughfinder(data, thresh=0.4, dist=250):
    """
    Finds troughs in `data`

    Parameters
    ----------
    data : array-like
    thresh : float (0,1)
    dist : int
        Minimum required distance (in datapoints) b/w troughs

    Returns
    -------
    array : trough locations (indices)
    """

    locs = get_extrema(data,peaks=False,thresh=thresh)
    locs = min_peak_dist(locs,data,peaks=False,dist=dist)

    return np.array(sorted(locs))


def check_troughs(data, troughs, peaks):
    """
    Confirms that a trough exists between every set of `peaks` in `data`

    Parameters
    ----------
    data : array-like
    troughs : array-like
        Location of current troughs
    peaks : array-like
        Location of peaks

    Returns
    -------
    array : troughs
    """

    trough_first = troughs.min() < peaks.min()
    trough_last  = troughs.max() > peaks.max()

    all_troughs = np.zeros(peaks.size-1 + trough_first + trough_last,
                           dtype='int64')

    if trough_first: all_troughs[0] = troughs[0]
    if trough_last: all_troughs[-1] = troughs[-1]

    for f in range(peaks.size-1):
        curr = np.logical_and(troughs>peaks[f],troughs<peaks[f+1])
        if not np.any(curr):
            dp = data[peaks[f]:peaks[f+1]]
            idx = peaks[f] + np.where(dp == dp.min())[0][0]
        else:
            idx = troughs[curr]
            if idx.size > 1: idx = idx[0]

        if trough_first: all_troughs[f+1] = idx
        else: all_troughs[f] = idx

    return all_troughs


def gen_temp(data, locs, factor=0.5):
    """
    Generate waveform template array from `data`

    Waveforms are taken from ~ `locs`

    Parameters
    ----------
    data : array-like
    locs : peak locations
    factor: float (0,1)

    Returns
    -------
    array : peak waveforms
    """

    avgrate = round(np.diff(locs).mean())

    THW       = int(round(factor*(avgrate/2)))
    nsamptemp = THW*2 + 1
    npulse    = locs.size
    template  = np.zeros([npulse-2,nsamptemp])

    for n in range(1,npulse-1):
        template[n-1] = data[locs[n]-THW:locs[n]+THW+1]
        template[n-1] = template[n-1] - template[n-1].mean()
        template[n-1] = template[n-1]/max(abs(template[n-1]))

    return template


def z_transform(z):
    """
    Z-transform `z`

    Parameters
    ----------
    z : array-like

    Returns
    -------
    array : z-transformed input
    """

    z = z - z.sum()/z.size
    z = z/np.sqrt(np.dot(z.T,z) * (1/(z.size-1)))

    return z


def corr(x, y, z_tran=[False,False]):
    """
    Returns correlation of `x` and `y`

    Parameters
    ----------
    x : array, n x 1
    y : array, n x 1
    z_tran : [bool, bool]
        Whether x and y, respectively, have been z-transformed already

    Returns
    -------
    float : [0,1] correlation between `x` and `y`
    """

    if x.ndim > 1: x = x.flatten()
    if y.ndim > 1: y = y.flatten()

    if not z_tran[0]: x = z_transform(x)
    if not z_tran[1]: y = z_transform(y)

    if x.size == y.size: return np.dot(x.T,y) * (1/(x.size-1))
    else: return None


def corr_template(temp, sim=0.95):
    """
    Generates single waveform template from `temp` array

    Parameters
    ----------
    temp : array of waveforms
    sim : float (0,1)
        Cutoff for correlation of waveforms to average template

    Returns
    -------
    array : template waveform
    """

    mean_temp = z_transform(temp.mean(axis=0))
    sim_to_temp = np.zeros((temp.shape[0],1))

    for n in range(temp.shape[0]):
        sim_to_temp[n] = corr(temp[n],mean_temp,[False,True])

    clean_temp = temp[np.where(sim_to_temp>sim)[0]]

    return clean_temp.mean(axis=0)


def update_match_temp(data,locs,temp):

    pass

def match_temp(data):
    """
    This currently doesn't work at all don't use this
    """

    locs = peakfinder(data,dist=round(np.diff(peakfinder(data)).mean())*0.5)
    avgrate = round(np.diff(locs).mean())
    temp = corr_template(data)

    idx = [0,20]
    THW = int(np.floor(temp.size/2))
    z_temp = z_transform(temp)[:int(THW*2)]
    is_z_trans = [0,1]

    c_samp_start = int(round(2*THW+1))
    try: c_samp_end = int(locs[idx[1]])
    except: c_samp_end = int(locs[-1])

    sim_to_temp = np.zeros(c_samp_end)
    for n in np.arange(c_samp_start,c_samp_end):
        i_sig_start = n - THW
        i_sig_end   = n + THW
        sig_part    = data[int(i_sig_start):int(i_sig_end)]

        sim_to_temp[n] = corr(sig_part,z_temp,is_z_trans)

    c_best_match = max(sim_to_temp)
    i_best_match = np.where(sim_to_temp==c_best_match)[0][0]

    peak_num = 0
    search_steps_tot = int(round(0.5*avgrate))
    n_samp_pad = THW + search_steps_tot
    data_padded = np.hstack((np.zeros(int(n_samp_pad)),
                             data,
                             np.zeros(int(n_samp_pad))))
    n = int(i_best_match + n_samp_pad)
    sim_to_temp = np.zeros(data_padded.size)

    while n > 1+search_steps_tot+THW:
        for search_pos in np.arange(-search_steps_tot,search_steps_tot,dtype='int64'):
            index_search_start = n - THW + search_pos
            index_search_end   = n + THW + search_pos
            sig_part = data_padded[int(index_search_start):int(index_search_end)]

            correlation = corr(sig_part,z_temp,is_z_trans)
            curr_weight = abs(data_padded[n+search_pos])
            correlation_weighted = curr_weight * correlation
            sim_to_temp[n+search_pos] = correlation_weighted

        index_search_start = n - search_steps_tot
        index_search_end   = n + search_steps_tot

        index_search_range = np.arange(index_search_start,index_search_end+1,dtype='int64')
        search_range_values = sim_to_temp[index_search_range]
        c_best_match = max(search_range_values)
        i_best_match = np.where(search_range_values==c_best_match)[0][0]
        best_pos = index_search_range[i_best_match]
        n = int(best_pos - avgrate)

    n = best_pos
    peak_num = 0
    cpulse = np.zeros(data.size)
    search_steps_tot = round(0.5*avgrate)
    location_weight = gaussian(2*search_steps_tot+1,
                               std=(2*search_steps_tot-1)/5)
    nlimit = data_padded.size - THW - search_pos

    while n < nlimit:
        for search_pos in np.arange(-search_steps_tot,search_steps_tot,dtype='int64'):
            index_search_start = max(0, n - THW + search_pos)
            index_search_end   = n + THW + search_pos
            sig_part = data_padded[int(index_search_start):int(index_search_end)]

            correlation = corr(sig_part,z_temp,is_z_trans)
            loc_weight = location_weight[search_pos+search_steps_tot]
            amp_weight = abs(data_padded[n+search_pos])
            correlation_weighted = amp_weight * correlation * loc_weight
            sim_to_temp[n+search_pos] = correlation_weighted

        index_search_start = n - search_steps_tot
        index_search_end   = n + search_steps_tot

        index_search_range = np.arange(index_search_start,index_search_end,dtype='int64')
        search_range_values = sim_to_temp[index_search_range]
        c_best_match = max(search_range_values)
        i_best_match = np.where(search_range_values==c_best_match)[0][0]
        best_pos = index_search_range[i_best_match]

        cpulse[peak_num] = best_pos - n_samp_pad
        peak_num += 1

        found_c_pulses = max(np.where(cpulse)[0])

        if found_c_pulses < 3: curr_hr_in_samp = avgrate
        if found_c_pulses < 21 and found_c_pulses >= 3: curr_hr_in_samp = round(np.mean(np.diff(cpulse)))
        if found_c_pulses >= 21:
            curr_cpulses = cpulse[int(found_c_pulses-20):int(found_c_pulses)]
            curr_hr_in_samp = round(np.mean(np.diff(curr_cpulses)))

        check_smaller = curr_hr_in_samp > 0.5*avgrate
        check_larger = curr_hr_in_samp < 1.5*avgrate

        if check_smaller and check_larger: n = int(best_pos + curr_hr_in_samp)
        else: n = int(best_pos + avgrate)

    return cpulse[np.where(cpulse)[0]]
