# -*- coding: utf-8 -*-

import numpy as np
import pytest

from peakdet.physio import Physio
from peakdet.tests import utils as testutils

DATA = np.loadtxt(testutils.get_test_data_path("ECG.csv"))
PROPERTIES = ["data", "fs", "history", "peaks", "troughs", "_masked"]
PHYSIO_TESTS = [
    # accepts "correct" inputs for history
    dict(kwargs=dict(data=DATA, history=[("good", "history")])),
    # fails on bad inputs for history
    dict(kwargs=dict(data=DATA, history=["malformed", "history"]), raises=TypeError),
    dict(kwargs=dict(data=DATA, history="not real history"), raises=TypeError),
    # accepts "correct" for metadata
    dict(kwargs=dict(data=DATA, metadata=dict())),
    dict(kwargs=dict(data=DATA, metadata=dict(peaks=[], reject=[], troughs=[]))),
    # fails on bad inputs for metadata
    dict(kwargs=dict(data=DATA, metadata=[]), raises=TypeError),
    dict(kwargs=dict(data=DATA, metadata=dict(peaks={})), raises=TypeError),
    # fails on bad inputs for data
    dict(kwargs=dict(data=np.column_stack([DATA, DATA])), raises=ValueError),
    dict(kwargs=dict(data="hello"), raises=ValueError),
]


def test_physio():
    phys = Physio(DATA, fs=1000)
    assert len(np.hstack((phys[:10], phys[10:-10], phys[-10:])))
    assert str(phys) == "Physio(size=44611, fs=1000.0)"
    assert len(np.exp(phys)) == 44611


class TestPhysio:
    tests = PHYSIO_TESTS

    def test_physio_creation(self):
        for test in PHYSIO_TESTS:
            if test.get("raises") is not None:
                with pytest.raises(test["raises"]):
                    phys = Physio(**test["kwargs"])
            else:
                phys = Physio(**test["kwargs"])
                for prop in PROPERTIES:
                    assert hasattr(phys, prop)
                for prop in ["peaks", "reject", "troughs"]:
                    assert isinstance(phys._metadata.get(prop), np.ndarray)


# TODO: Update unit test
def test_neurokit2phys(path_neurokit):
    df = pd.read_csv(path_neurokit, sep="\t")  # noqa
    phys = Physio.neurokit2phys(
        path_neurokit, copy_data=True, copy_peaks=True, copy_troughs=True, fs=fs  # noqa
    )

    assert all(
        np.unique(
            phys.data
            == np.hstack(df.loc[:, df.columns.str.endswith("Clean")].to_numpy())
        )
    )
    assert all(
        np.unique(
            phys.peaks == np.where(df.loc[:, df.columns.str.endswith("Peaks")] != 0)[0]
        )
    )
    assert phys.fs == fs  # noqa


# TODO: Update unit test
def test_phys2neurokit(path_phys):
    phys = load_physio(path_phys, allow_pickle=True)  # noqa
    neuro = data.phys2neurokit(  # noqa
        copy_data=True,
        copy_peaks=True,
        copy_troughs=False,
        module=module,  # noqa
        neurokit_path=path_neurokit,  # noqa
    )

    assert all(
        np.unique(
            phys.data
            == np.hstack(neuro.loc[:, neuro.columns.str.endswith("Raw")].to_numpy())
        )
    )
    assert all(
        np.unique(
            phys.peaks
            == np.where(neuro.loc[:, neuro.columns.str.endswith("Peaks")] != 0)[0]
        )
    )
