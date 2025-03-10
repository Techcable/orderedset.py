import random
from typing import Any, TypeVar

from techcable.orderedset import OrderedSet

T = TypeVar("T")


def _remove_duplicates(l: list[T]) -> list[T]:
    seen = set()
    res = []
    for item in l:
        if item not in seen:
            res.append(item)
        seen.add(item)
    return res


EXAMPLE_DATA: list[list[Any]] = [
    ["foo", "bar", "baz", "foo"],
    [1, 2, 7, 13, 9, 12, 2, 8, 7],
    [float("NaN"), 2.8, float("NaN"), 7.9],
]


def test_simple():
    for data in EXAMPLE_DATA:
        oset = OrderedSet(data)
        assert _remove_duplicates(data) == list(oset)
        assert set(data) == oset
        assert set(data) == set(oset)


def test_remove():
    for orig_data in EXAMPLE_DATA:
        data = orig_data.copy()
        orig_oset = OrderedSet(orig_data)
        oset = orig_oset.copy()
        target = random.choice(data)
        oset.remove(target)
        while target in data:
            data.remove(target)
        assert orig_oset == OrderedSet(orig_data), "Copy didn't work"
        assert oset == (orig_oset - {target})
        assert oset == OrderedSet(data)
