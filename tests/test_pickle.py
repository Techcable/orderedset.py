import pickle
from pathlib import Path

import pytest

from techcable.orderedset import OrderedSet


def test_pickle_roundtrip():
    original = OrderedSet([1, 2, 3, 4, 7, 1])
    ser = pickle.dumps(original)
    deser = pickle.loads(ser)
    assert original == deser


_LATEST_DATA_VERSION = "v0.1.5"
"""The current version of the data being stored"""


def _load_data(name: str, /, *, version: str) -> bytes:
    return (Path(__file__).parent / f"data/pickle/{name}-{version}.dat").read_bytes()


@pytest.mark.parametrize("version", ["v0.1.4"])
@pytest.mark.parametrize("data", ["example1"])
def test_unpickle_backwards_compat(version: str, data: str):
    """Verify we can still unpickle from old versions"""
    current_data = _load_data(data, version=_LATEST_DATA_VERSION)
    old_data = _load_data(data, version=version)
    current = pickle.loads(current_data)
    old = pickle.loads(old_data)
    assert old == current
