"""Print unique lines, preserving order.

This is intended as a order-preserving alternative to `sort | uniq`,
and a demonstration of techcable.OrderedSet functionality.
Unlike `sort | uniq` it will immediately output lines as soon as they are received,
without needing to wait for all input.

It is only runnable as a python module (`python -m techcable.orderedset`)
so it will not conflict with other commands or pollute your path.

The functionality in this module is not intended for use as an API"""

from __future__ import annotations

import argparse
import sys
from typing import IO, TypeVar, no_type_check

from . import OrderedSet


def _disable_traceback(disabled_type: type[BaseException], /) -> None:
    """Disable traceback printing for a specific exception type"""
    orig_excepthook = sys.excepthook

    @no_type_check
    def _filter_excepthook(type, value, traceback):
        if issubclass(type, disabled_type):
            pass  # do not print
        else:
            orig_excepthook(type, value, traceback)

    sys.excepthook = _filter_excepthook


S = TypeVar("S", str, bytes)


def _dedup_stream(input_file: IO[S], output_file: IO[S], /) -> None:
    assert input_file.readable()
    assert output_file.writable()
    oset: OrderedSet[S] = OrderedSet()
    while line := input_file.readline():
        # OrderedSet.append returns True if the item is newly added,
        # and False if it already exists
        if oset.append(line):
            output_file.write(line)


def _main(raw_args: list[str] | None = None, /) -> None:
    _disable_traceback(KeyboardInterrupt)
    parser = argparse.ArgumentParser(
        prog="techcable.orderedset", description="Print unique lines, preserving order"
    )
    parser.add_argument(
        "input_file",
        type=argparse.FileType(mode="br"),
        help="The input file to read from",
        nargs="?",
        default="-",
    )

    args = parser.parse_args(raw_args)
    _dedup_stream(args.input_file, sys.stdout.buffer)


if __name__ == "__main__":
    _main()

__all__ = ()
