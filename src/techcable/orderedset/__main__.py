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
import os
import sys
from collections.abc import Iterator
from typing import IO, Iterable, Never, TypeVar, no_type_check

from . import OrderedSet


def _fatal(msg: str) -> Never:
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(1)


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


def _read_lines(input_file: IO[S], /) -> Iterator[S]:
    if not input_file.readable():
        raise TypeError("input not readable")
    while True:
        try:
            line = input_file.read()
        except IOError as e:
            _fatal(f"Failed to read input, {e}")
        if line:
            yield line
        else:
            break


def _write_lines(output_file: IO[S], lines: Iterable[S], /) -> None:
    if not output_file.writable():
        raise TypeError("output not writable")
    for line in lines:
        try:
            output_file.write(line)
            output_file.flush()
        except IOError as e:
            _fatal(f"Failed to write output, {e}")


def _dedup_stream(input_file: IO[S], output_file: IO[S], /) -> None:
    # uses OrderedSet.dedup to deduplicate
    _write_lines(output_file, OrderedSet.dedup(_read_lines(input_file)))


def _open_raw_input(input_file: str | None) -> IO[bytes]:
    if input_file is None or input_file == "-":
        return os.fdopen(sys.stdin.fileno(), "rb", buffering=0)
    else:
        try:
            return open(input_file, "rb", buffering=0)
        except FileNotFoundError:
            _fatal(f"File not found: {input_file}")
        except IOError as e:
            _fatal(f"Failed to open file, {e}")


def _main(raw_args: list[str] | None = None, /) -> None:
    _disable_traceback(KeyboardInterrupt)
    parser = argparse.ArgumentParser(
        prog="techcable.orderedset", description="Print unique lines, preserving order"
    )
    parser.add_argument(
        "input_file",
        help="The input file to read from",
        nargs="?",
        default="-",
    )

    args = parser.parse_args(raw_args)
    with _open_raw_input(args.input_file) as input_file:
        _dedup_stream(input_file, os.fdopen(sys.stdout.fileno(), "wb", buffering=0))


if __name__ == "__main__":
    _main()

__all__ = ()
