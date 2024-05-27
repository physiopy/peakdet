# -*- coding: utf-8 -*-
"""
Helper class for holding physiological data and associated metadata inforamtion
"""

import numpy as np
from loguru import logger


class Physio:
    """
    Class to hold physiological data and relevant information

    Parameters
    ----------
    data : array_like
        Input data array
    fs : float, optional
        Sampling rate of `data` (Hz). Default: None
    history : list of tuples, optional
        Functions performed on `data`. Default: None
    metadata : dict, optional
        Metadata associated with `data`. Default: None
    suppdata : array_like, optional
        Support data array. Default: None

    Attributes
    ----------
    data : :obj:`numpy.ndarray`
        Physiological waveform
    fs : float
        Sampling rate of `data` in Hz
    history : list of tuples
        History of functions that have been performed on `data`, with relevant
        parameters provided to functions.
    peaks : :obj:`numpy.ndarray`
        Indices of peaks in `data`
    troughs : :obj:`numpy.ndarray`
        Indices of troughs in `data`
    suppdata : :obj:`numpy.ndarray`
        Secondary physiological waveform
    """

    def __init__(self, data, fs=None, history=None, metadata=None, suppdata=None):
        self._data = np.asarray(data).squeeze()
        if self.data.ndim > 1:
            # raise ValueError('Provided data dimensionality {} > 1.'
            #                  .format(self.data.ndim))
            raise ValueError(
                logger.exception(
                    "Provided data dimensionality {} > 1.".format(self.data.ndim)
                )
            )

        if not np.issubdtype(self.data.dtype, np.number):
            raise ValueError(
                "Provided data of type {} is not numeric.".format(self.data.dtype)
            )
        self._fs = np.float64(fs)
        self._history = [] if history is None else history
        if not isinstance(self._history, list) or any(
            [not isinstance(f, tuple) for f in self._history]
        ):
            raise TypeError(
                "Provided history {} must be a list-of-tuples. "
                "Please check inputs.".format(history)
            )
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError(
                    "Provided metadata {} must be dict-like.".format(metadata)
                )
            for k in ["peaks", "troughs", "reject"]:
                metadata.setdefault(k, np.empty(0, dtype=int))
                if not isinstance(metadata.get(k), np.ndarray):
                    try:
                        metadata[k] = np.asarray(metadata.get(k), dtype=int)
                    except TypeError:
                        raise TypeError(
                            "Provided metadata must be dict-like"
                            "with integer array entries."
                        )
            self._metadata = dict(**metadata)
        else:
            self._metadata = dict(
                peaks=np.empty(0, dtype=int),
                troughs=np.empty(0, dtype=int),
                reject=np.empty(0, dtype=int),
            )
        self._suppdata = None if suppdata is None else np.asarray(suppdata).squeeze()

    def __array__(self):
        return self.data

    def __getitem__(self, slicer):
        return self.data[slicer]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "{name}(size={size}, fs={fs})".format(
            name=self.__class__.__name__, size=self.data.size, fs=self.fs
        )

    __repr__ = __str__

    @property
    def data(self):
        """Physiological data"""
        return self._data

    @property
    def fs(self):
        """Sampling rate of data (Hz)"""
        return self._fs

    @property
    def history(self):
        """Functions that have been performed on / modified `data`"""
        return self._history

    @property
    def peaks(self):
        """Indices of detected peaks in `data`"""
        return self._masked.compressed()

    @property
    def troughs(self):
        """Indices of detected troughs in `data`"""
        return self._metadata["troughs"]

    @property
    def _masked(self):
        return np.ma.masked_array(
            self._metadata["peaks"],
            mask=np.isin(self._metadata["peaks"], self._metadata["reject"]),
        )

    @property
    def suppdata(self):
        """Physiological data"""
        return self._suppdata

    def phys2neurokit(
        self, copy_data, copy_peaks, copy_troughs, module, neurokit_path=None
    ):
        """Physio to neurokit dataframe

        Parameters
        ----------
        copy_data: bool
            whether to copy raw data from Physio object to dataframe
        copy_peaks: bool
            whether to copy peaks from Physio object to dataframe
        copy_troughs: bool
            whether to copy troughs from Physio object to dataframe
        module: string
            name of module (eg. 'EDA', 'RSP', 'PPG'...)
        neurokit_path: string
            path to neurokit dataframe
        """
        import pandas as pd

        if neurokit_path is not None:
            df = pd.read_csv(neurokit_path, sep="\t")
        else:
            df = pd.DataFrame(
                0,
                index=np.arange(len(self.data)),
                columns=["%s_Raw" % module, "%s_Peaks" % module, "%s_Troughs" % module],
            )

        if copy_data:
            df.loc[:, df.columns.str.endswith("Raw")] = self.data

        if copy_peaks:
            b_peaks = np.zeros(len(self.data))
            b_peaks[self.peaks] = 1
            df.loc[:, df.columns.str.endswith("Peaks")] = b_peaks

        if copy_troughs:
            b_troughs = np.zeros(len(self.data))
            b_troughs[self.troughs] = 1
            df.loc[:, df.columns.str.endswith("Troughs")] = b_troughs

        return df

    @classmethod
    def neurokit2phys(
        cls, neurokit_path, fs, copy_data, copy_peaks, copy_troughs, **kwargs
    ):
        """Neurokit dataframe to phys

        Parameters
        ----------
        neurokit_path: string
            path to neurokit dataframe
        fs: float
            sampling rate
        copy_data: bool
            whether to copy raw data from Physio object to dataframe
        copy_peaks: bool
            whether to copy peaks from Physio object to dataframe
        copy_troughs: bool
            whether to copy troughs from Physio object to dataframe
        suppdata: array_like, optional
            Support data array. Default: None
        """
        import pandas as pd

        df = pd.read_csv(neurokit_path, sep="\t")

        if copy_data:
            # if cleaned data exists, substitute 'data' with cleaned data, else use raw data
            if df.columns.str.endswith("Clean").any():
                data = np.hstack(df.loc[:, df.columns.str.endswith("Clean")].to_numpy())
            elif df.columns.str.endswith("Raw").any():
                data = np.hstack(df.loc[:, df.columns.str.endswith("Raw")].to_numpy())

        if copy_peaks:
            # if peaks exists
            if df.columns.str.endswith("Peaks").any():
                peaks = np.where(df.loc[:, df.columns.str.endswith("Peaks")] == 1)[0]

        if copy_troughs:
            # if troughs exists
            if df.columns.str.endswith("Troughs").any():
                troughs = np.where(df.loc[:, df.columns.str.endswith("Troughs")] == 1)[
                    0
                ]

        if "peaks" in locals() and "troughs" in locals():
            metadata = dict(peaks=peaks, troughs=troughs)
        elif "peaks" in locals() and "troughs" not in locals():
            metadata = dict(peaks=peaks)

        return cls(data, fs=fs, metadata=metadata, **kwargs)
