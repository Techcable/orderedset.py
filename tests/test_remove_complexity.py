"""
Ensures the [`OrderedSet.remove`] function runs in constant time instead of linear time.
"""

import threading
from typing import ClassVar

import pytest

from techcable.orderedset import OrderedSet


class UnexpectedComplexityError(AssertionError):
    pass


class EqualityCounter(threading.local):
    comparisons: int
    hashes: int = 0

    def __init__(self) -> None:
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.comparisons = 0
        self.hashes = 0


class EqualityCounted:
    """A type that counts the number of times it has been compared against."""

    value: int
    COUNTER: ClassVar = EqualityCounter()

    def __init__(self, value: int, /):
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EqualityCounted):
            self.COUNTER.comparisons += 1
            return self.value == other.value
        else:
            return NotImplemented

    def __hash__(self) -> int:
        self.COUNTER.hashes += 1
        return hash(self.value)

    def __repr__(self) -> str:
        return f"EqualityCounter({self.value})"


@pytest.mark.xfail(raises=UnexpectedComplexityError, reason="Remove is still linear")
def test_const_remove():
    oset = OrderedSet(EqualityCounted(i) for i in range(10_000))
    EqualityCounted.COUNTER.reset()
    oset.remove(EqualityCounted(5000))
    if (comparison_count := EqualityCounted.COUNTER.comparisons) > 10:
        raise UnexpectedComplexityError(f"oset.remove: {comparison_count}")
