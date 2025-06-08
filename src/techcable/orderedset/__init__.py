"""
Implements `OrderedSet`, a [`MutableSet`] that preserves insertion order and is also a [`Sequence`].

[`MutableSet`]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet
[`Sequence`]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence

The implementation is pure-python and does not require any native code.
"""

from ._orderedset import OrderedSet
from ._version import __version__

__all__ = (
    "OrderedSet",
    "__version__",
)
