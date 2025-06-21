from __future__ import annotations

import operator
from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    Callable,
    Generator,
    Iterable,
    Iterator,
    MutableSet,
    Sequence,
    Set,
)
from typing import TYPE_CHECKING, Any, TypeVar, overload

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import core_schema
    from typing_extensions import Protocol, get_args, override

    class Comparable(Protocol):  # noqa: PLW1641 - do not require __hash__ method
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
    """
    A [`MutableSet`] that preserves insertion order and is also a [`Sequence`].

    ## Conveniences
    Calling [`OrderedSet.append`] returns `True` if the element was successfully added,
    and `False` if the element is a duplicate.

    Calling [`OrderedSet.__str__`]` is equivalent to `f"{x!r, y!r}"`.
    This is much prettier than [`OrderedSet.__repr__`],
    which is expected to roundtrip through `eval`.

    ## Gotchas
    This type does not implement [`MutableSequence`]
    because [`OrderedSet.append`] ignores duplicate elements
    and returns `bool` instead of `None`.

    The [`OrderedSet.remove`] method takes linear time to remove an element,
    not constant time like `set.remove` does.
    Calling it in a loop will trigger quadratic blow up just like use of [`list.remove`] would.
    To avoid this, bulk-remove elements using the set subtraction operator (`-=`).

    ### Thread Safety
    This type is *NOT* safe to mutate from multiple threads.

    Concurrent reads are fully supported,
    as long as no modifications are being made.
    """

    __slots__ = ("_elements", "_unique")

    _unique: set[T]
    _elements: list[T]

    @override
    def __init__(self, source: Iterable[T] | None = None, /) -> None:
        """
        Create an `OrderedSet` containing the specified elements.

        This preserves the order of the original input and implicitly ignores duplicates.
        """
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

    @classmethod
    def of(cls, /, *args: T) -> OrderedSet[T]:
        """
        Construct an [`OrderedSet`] using specified elements.

        This is a factory method equivalent to `OrderedSet([*args])`,
        but avoiding an extra pair of brackets.

        It is inspired by Java's [`List.of`] method.

        Unlike the java method, the returned set is not immutable.
        It is no different from those produced using the standard constructor.

        [`List.of`]: https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/List.html#of(E...)
        """
        return cls(args)

    def append(self, value: T, /) -> bool:
        """
        Append a value to the set, returning `True` if successfully added.

        Returns `False` if the element already exists.

        There are two important differences between this method and [`list.append`]:
        1. This method does nothing if the value is a duplicate
        2. This method returns a `bool` instead of `None`
        """
        is_new = value not in self._unique
        if is_new:
            self._unique.add(value)
            self._elements.append(value)
        assert len(self._unique) == len(self._elements)
        return is_new

    def extend(self, values: Iterable[T], /) -> bool:
        """
        Add all the specified values to the set.

        Returns `True` if at least one element was added,
        or `False` if every element is a duplicate.

        Equivalent to `any(oset.append(v) for v in values)`.
        """
        changed = False
        for val in values:
            changed |= self.append(val)
        return changed

    @override
    def add(self, value: T, /) -> None:
        """
        Add a value to the set if it doesn't already exist.

        Return value is `None` for consistency with [`set.add`].
        Use [`OrderedSet.append`] if you want to know if the element already existed.
        """
        self.append(value)

    @override
    def remove(self, value: T, /) -> None:
        """
        Remove an element from the set, throwing a KeyError if not present.

        This method preserves the original order of the set.
        However, it takes linear time like [`list.remove`],
        instead of the constant time that [`set.remove`] takes.
        Invoking it repeatedly may cause quadratic blowup, just like `list.remove` would.

        See [`OrderedSet.discard`] for a variant that does nothing if the item is not present.
        """
        # set.remove will raise a KeyError for us
        self._unique.remove(value)
        self._elements.remove(value)

    @override
    def discard(self, value: T, /) -> None:
        """
        Remove an element from the set if it exists.

        This method preserves the original order of the set.
        However, it takes linear time (`O(n)`) instead of the constant time.
        Invoking it repeatedly may cause quadratic blowup.
        See [`OrderedSet.remove`] for more details on this.

        Unlike [`OrderedSet.remove`], this method does not raise
        an exception if this element is missing.
        """
        if value in self._unique:
            self._elements.remove(value)
            self._unique.remove(value)

    def update(self, values: Iterable[T], /) -> None:
        """
        Add all the specified values to this set.

        Equivalent to running
        ```
        for val in values:
            oset.add(val)
        ```
        """
        self.extend(values)

    @override
    def pop(self, index: int = -1) -> T:
        """
        Remove and return an item from the end of the list (or from `self[index]`).

        Raises `IndexError` if the list is empty or `index` is out of bounds.

        Equivalent to [`list.pop`].
        """
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

    __hash__ = None  # type: ignore
    """Since an OrderedSet is mutable, it does is not hashable."""

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

    def sort(self, *, key: Callable[[T], U] | None = None, reverse: bool = False) -> None:
        """Sort the elements of the set in-place, as if calling [`list.sort`]."""
        self._elements.sort(key=key, reverse=reverse)

    def reverse(self) -> None:
        """Reverse the elements of the set in-place, as if calling [`list.reverse`]."""
        self._elements.reverse()

    def copy(self) -> OrderedSet[T]:
        """
        Create a shallow copy of the set.

        Equivalent to `OrderedSet(self)`.
        """
        return OrderedSet(self)

    @override
    def __repr__(self) -> str:
        """
        Represent this set in a form that will round-trip through [`eval`].

        Examples:
        - `repr(OrderedSet([1, 2, 3]))` returns `"OrderedSet([1, 2, 3])"`
        - `repr(OrderedSet([1, 2, 3]))` returns `"OrderedSet([1, 2"])`

        The representation used by [`OrderedSet.__str__`] is much prettier.
        It still calls `repr` on each element and not `str`,
        so `str(OrderedSet([' '])` gives `"{' '}"` instead of `"{ }"`.
        It is really just a prettier `repr` which isn't contained
        by the need to round-trip through [`eval`].

        The format changed in v0.1.6 to take advantage of [`OrderedSet.of`].
        It now uses `"OrderedSet.of(1,2,3)"` instead of OrderedSet([1,2,3])`.
        This may break users relying on the format,
        but I consider this acceptable during the beta.
        """
        # by convention, this should roundtrip through eval
        return f"OrderedSet.of({', '.join(map(repr, self))})"

    @override
    def __str__(self) -> str:
        """
        Represent the elements in this set by calling `repr` on each element, surrounding it with braces.

        Examples:
        - `str(OrderedSet([1, 2, 3]))` returns `"{1, 2, 3}"`
        - `str(OrderedSet(["a", "b", "c"]))` returns `"{'a', 'b', 'c'}"`

        This would make a very good implementation of [`OrderedSet.__repr__`],
        except for the fact it will not round-trip through [`eval`].
        """
        return f"{{{', '.join(map(repr, self))}}}"

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        # See here: https://docs.pydantic.dev/latest/concepts/types/#generic-containers
        instance_schema = core_schema.is_instance_schema(cls)

        args = get_args(source_type)
        if args:
            # replace the type and rely on Pydantic to generate the right schema for `Sequence`
            target_type: type = Sequence[args[0]]  # type: ignore
            sequence_t_schema = handler.generate_schema(target_type)
        else:
            sequence_t_schema = handler.generate_schema(Sequence)

        non_instance_schema = core_schema.no_info_after_validator_function(OrderedSet, sequence_t_schema)
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

    def __getstate__(self) -> Any:
        """Efficiently pickles the elements of an OrderedSet."""
        assert len(self._elements) == len(self._unique)
        # format for v0.1.5
        return self._elements.copy()

    def __setstate__(self, state: Any) -> None:
        """Restores the elements of an OrderedSet from the pickled representation."""
        # init variables
        self._unique = set()
        self._elements = []
        # deserialize `state` - a poor man's `match`
        elements: list[T]
        if isinstance(state, list):
            # format for v0.1.5 - list of elements
            elements = state
        elif isinstance(state, tuple) and len(state) == 2:
            state_dict, state_slots = state
            if state_dict is not None:
                raise TypeError
            # format for v0.1.4 - (None, dict(_elements=..., _unique=...))
            elements = state_slots["_elements"]
            if set(elements) != state_slots["_unique"]:
                raise ValueError("Fields `_elements` and `_unique` must match")
        else:
            raise TypeError(f"Cannot unpickle from {type(state)}")
        # set elements
        self.update(elements)

    @classmethod
    def dedup(cls, source: Iterable[T], /) -> Generator[T]:
        """
        Yield unique elements, preserving order.

        This is an iterator combinator (generator) similar to those in [`itertools`].
        It does not need to wait for the entire input,
        and will return items as soon as they are available.

        This is similar to [`more_itertools.unique_everseen`],
        although it uses an `OrderedSet` internally and does not support the `key` argument.

        Since: v0.1.4

        [`more_itertools.unique_everseen`]: https://more-itertools.readthedocs.io/en/v10.7.0/api.html#more_itertools.unique_everseen
        """
        oset: OrderedSet[T] = OrderedSet()
        for item in source:
            if oset.append(item):
                # new value
                yield item

    @classmethod
    async def dedup_async(cls, source: AsyncIterable[T], /) -> AsyncGenerator[T]:
        """
        Yield unique elements, preserving order.

        This is an iterator combinator (generator) similar to those in [`itertools`].
        It does not need to wait for the entire input,
        and will return items as soon as they are available.
        Because it is asynchronous, it does not block the thread while waiting.

        This is an asynchronous version of [`OrderedSet.dedup`].

        It is similar to [`more_itertools.unique_everseen`],
        but is asynchronous, uses an `OrderedSet` internally,
        and does not support the `key` argument.

        Since: v0.1.4

        [`more_itertools.unique_everseen`]: https://more-itertools.readthedocs.io/en/v10.7.0/api.html#more_itertools.unique_everseen
        """
        # async for defined in PEP 525
        oset: OrderedSet[T] = OrderedSet()
        async for item in source:
            if oset.append(item):
                # new value
                yield item


__all__ = ("OrderedSet",)
