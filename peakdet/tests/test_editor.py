from collections import namedtuple

import pytest

from peakdet import editor
from peakdet.tests.utils import get_peak_data

wheel = namedtuple("wheel", ("step"))
key = namedtuple("key", ("key",))


def test_PhysioEditor():
    edits = editor._PhysioEditor(get_peak_data())

    # test scroll functionality
    edits.on_wheel(wheel(10))

    # test reject / delete functionality
    for _m in range(2):
        edits.on_remove(0, 10, reject=True)
        edits.on_remove(10, 20, reject=False)

    # undo delete + reject
    for _m in range(2):
        edits.undo()

    # test key undo (and undo when history doesn't exist)
    edits.on_key(key("ctrl+z"))

    # redo so that there is history on quit
    edits.on_remove(0, 10, reject=True)
    edits.on_remove(10, 20, reject=False)

    # quit editor and clean up edits
    edits.on_key(key("ctrl+z"))

    with pytest.raises(TypeError):
        editor._PhysioEditor([0, 1, 2])
