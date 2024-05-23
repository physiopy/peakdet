__all__ = [
    'delete_peaks', 'edit_physio', 'filter_physio', 'interpolate_physio',
    'peakfind_physio', 'plot_physio', 'reject_peaks',
    'load_physio', 'save_physio', 'load_history', 'save_history',
    'load_rtpeaks', 'Physio', 'HRV', '__version__'
]

from peakdet.analytics import (HRV)
from peakdet.external import (load_rtpeaks)
from peakdet.io import (load_physio, save_physio, load_history, save_history)
from peakdet.operations import (delete_peaks, edit_physio, filter_physio,
                                interpolate_physio, peakfind_physio,
                                plot_physio, reject_peaks)
from peakdet.physio import (Physio)
from loguru import logger

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# TODO: Loguru does not detect the module's name
logger.disable(None)