from peakdet import load_physio, save_physio
from peakdet.operations import edit_physio, interpolate_physio, filter_physio, peakfind_physio

FUNCTION_MAPPINGS = {
    "interpolate_physio": interpolate_physio,
    "filter_physio": filter_physio,
    "peakfind_physio": peakfind_physio
}

def process_signals(data, steps):
    """
    Parameters
    ----------
    data : :class:`peakdet.Physio`
    steps : list

    Return
    ------
    data : :class:`peakdet.Physio` (w/ features from peakfind_physio)
    """
    for step in steps:
        func = list(step.keys())[0]
        data = FUNCTION_MAPPINGS[func](data, **step[func])
    return data


def manual_peaks(data, fname):
    """
    data : str or array_like or Physio_like
        Input physiological data. If array_like, should be one-dimensional
    fname : str
        Path to output file; .phys will be appended if necessary
    """
    # Load signals
    phys = load_physio(data, allow_pickle=True)
    # Edit peaks
    phys = edit_physio(data)
    # Save edits
    save_physio(fname, phys)