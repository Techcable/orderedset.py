from __future__ import annotations

import operator
from collections.abc import Callable, Iterable, Iterator, MutableSet, Sequence, Set
from typing import TYPE_CHECKING, Any, Optional, TypeVar, overload

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import core_schema
    from typing_extensions import Protocol, get_args, override

    class Comparable(Protocol):
        def __lt__(self, other: Comparable) -> bool:
            pass

        def __gt__(self, other: Comparable) -> bool:
            pass

        def __eq__(self, other: object) -> bool:
            pass


else:
    Comparable = object

    def override(v):
        return v

    try:
        from pydantic_core import core_schema
    except ImportError:
        pass

    try:
        # prefer typing_extensions.get_args for python3.9
        # needed for pydantic
        from typing_extensions import get_args
    except ImportError:
        from typing import get_args


T = TypeVar("T")
U = TypeVar("U", bound=Comparable)


class OrderedSet(MutableSet[T], Sequence[T]):
    """A Set of elements, which preserves insertion order.

    This type cannot implement `MutableSequence` because OrderedSet.append
    ignores duplicate elements and returns a `bool` instead of `None`."""

    __slots__ = ("_unique", "_elements")

    _unique: set[T]
    _elements: list[T]

    @override
    def __init__(self, source: Iterable[T] | None = None, /) -> None:
        """Create an ordered set containing the specified elements"""
        self._unique = set()
        self._elements = []
        if source is None:
            return
        elif isinstance(source, OrderedSet):
            self._unique = source._unique.copy()
            self._elements = source._elements.copy()
        elif isinstance(source, (set, frozenset)):
            self._unique = set(source)
            self._elements = list(source)
        else:
            for value in source:
                self.append(value)
        assert len(self._unique) == len(self._elements)

    def append(self, value: T, /) -> bool:
        """Append a value to the set if it doesn't already exist.

        Returns `True` if successfully added, or `False` if already exists.
        Note that the return value doesn't match list.append, which always returns `None`"""
        is_new = value not in self._unique
        if is_new:
            self._unique.add(value)
            self._elements.append(value)
        assert len(self._unique) == len(self._elements)
        return is_new

    def extend(self, values: Iterable[T], /) -> bool:
        """
        Add all the specified values to the set.

        Returns True if at least one element was added,
        or `False` if every element is a duplicate.

        Roughly equivalent to `any(oset.append(v) for v in values)`.
        """
        changed = False
        for val in values:
            changed |= self.append(val)
        return changed

    @override
    def add(self, value: T, /) -> None:
        """Add a value to the set if it doesn't already exist.

        Return value is `None` for consistency with `set.add`.
        Use `OrderedSet.append` if you want to know if the element already existed."""
        self.append(value)

    @override
    def discard(self, value: T, /) -> None:
        """Remove the element from the set if it exists."""
        if value in self._unique:
            self._elements.remove(value)
            self._unique.remove(value)

    def update(self, values: Iterable[T], /) -> None:
        """Add all the"""
        self.extend(values)

    @override
    def pop(self, index: int = -1) -> T:
        """Pop an item from the end of the list (or at `index`)"""
        item = self._elements.pop(index)
        self._unique.remove(item)
        return item

    @override
    def __iter__(self) -> Iterator[T]:
        assert len(self._unique) == len(self._elements)
        return iter(self._elements)

    @override
    def __reversed__(self) -> Iterator[T]:
        return self._elements.__reversed__()

    @override
    def __len__(self) -> int:
        return len(self._elements)

    @override
    def __contains__(self, item: object) -> bool:
        return item in self._unique

    @override
    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    @overload
    def __getitem__(self, index: slice) -> OrderedSet[T]: ...

    @override
    def __getitem__(self, index: int | slice) -> T | Sequence[T]:
        if isinstance(index, int):
            return self._elements[index]
        elif isinstance(index, slice):
            items = self._elements[index]
            as_set = OrderedSet(items)
            assert len(items) == len(as_set)
            return items
        else:
            return NotImplemented

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, OrderedSet):
            # ignores order, like a good set
            return self._unique == other._unique
        elif isinstance(other, Set):
            return self._unique == other
        else:
            return NotImplemented

    def _impl_cmp_op(self, other: object, op: Callable[[Any, Any], bool]) -> bool:
        if isinstance(other, OrderedSet):
            return op(self._unique, other._unique)
        elif isinstance(other, Sequence):
            return op(self, OrderedSet(other))
        else:
            # this makes mypy mad if we do it here (but it's fine in __lt__)
            return NotImplemented  # type: ignore

    @override
    def __lt__(self, other: object) -> bool:
        return self._impl_cmp_op(other, operator.lt)

    @override
    def __le__(self, other: object) -> bool:
        return self._impl_cmp_op(other, operator.le)

    @override
    def __gt__(self, other: object) -> bool:
        return self._impl_cmp_op(other, operator.gt)

    @override
    def __ge__(self, other: object) -> bool:
        return self._impl_cmp_op(other, operator.ge)

    def sort(
        self, key: Optional[Callable[[T], U]] = None, reverse: bool = False
    ) -> None:
        """Sort the elements in the set, as if calling list.sort"""
        self._elements.sort(key=key, reverse=reverse)

    def reverse(self) -> None:
        """Reverse the elements in the set, as if calling list.reverse"""
        self._elements.reverse()

    def copy(self) -> OrderedSet[T]:
        """Create a copy of the set"""
        return OrderedSet(self)

    @override
    def __repr__(self) -> str:
        # by convention, this should roundtrip through eval
        return f"OrderedSet([{', '.join(map(repr, self))}])"

    @override
    def __str__(self) -> str:
        return f"{{{', '.join(map(repr, self))}}}"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        # See here: https://docs.pydantic.dev/latest/concepts/types/#generic-containers
        instance_schema = core_schema.is_instance_schema(cls)

        args = get_args(source_type)
        if args:
            # replace the type and rely on Pydantic to generate the right schema for `Sequence`
            target_type: type = Sequence[args[0]]  # type: ignore
            sequence_t_schema = handler.generate_schema(target_type)
        else:
            sequence_t_schema = handler.generate_schema(Sequence)

        non_instance_schema = core_schema.no_info_after_validator_function(
            OrderedSet, sequence_t_schema
        )
        return core_schema.union_schema(
            [
                instance_schema,
                non_instance_schema,
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                list,  # OrderedSet -> list
                info_arg=False,
                return_schema=core_schema.list_schema(),
            ),
        )


__all__ = ("OrderedSet",)
