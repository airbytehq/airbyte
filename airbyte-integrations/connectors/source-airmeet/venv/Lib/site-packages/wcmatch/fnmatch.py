"""
Wild Card Match.

A custom implementation of `fnmatch`.
"""
from __future__ import annotations
from . import _wcparse
from typing import AnyStr, Iterable, Sequence

__all__ = (
    "CASE", "EXTMATCH", "IGNORECASE", "RAWCHARS",
    "NEGATE", "MINUSNEGATE", "DOTMATCH", "BRACE", "SPLIT",
    "NEGATEALL", "FORCEWIN", "FORCEUNIX",
    "C", "I", "R", "N", "M", "D", "E", "S", "B", "A", "W", "U",
    "translate", "fnmatch", "filter", "escape", "is_magic"
)

C = CASE = _wcparse.CASE
I = IGNORECASE = _wcparse.IGNORECASE
R = RAWCHARS = _wcparse.RAWCHARS
N = NEGATE = _wcparse.NEGATE
M = MINUSNEGATE = _wcparse.MINUSNEGATE
D = DOTMATCH = _wcparse.DOTMATCH
E = EXTMATCH = _wcparse.EXTMATCH
B = BRACE = _wcparse.BRACE
S = SPLIT = _wcparse.SPLIT
A = NEGATEALL = _wcparse.NEGATEALL
W = FORCEWIN = _wcparse.FORCEWIN
U = FORCEUNIX = _wcparse.FORCEUNIX

FLAG_MASK = (
    CASE |
    IGNORECASE |
    RAWCHARS |
    NEGATE |
    MINUSNEGATE |
    DOTMATCH |
    EXTMATCH |
    BRACE |
    SPLIT |
    NEGATEALL |
    FORCEWIN |
    FORCEUNIX
)


def _flag_transform(flags: int) -> int:
    """Transform flags to glob defaults."""

    # Enabling both cancels out
    if flags & FORCEUNIX and flags & FORCEWIN:
        flags ^= FORCEWIN | FORCEUNIX

    return (flags & FLAG_MASK)


def translate(
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> tuple[list[AnyStr], list[AnyStr]]:
    """Translate `fnmatch` pattern."""

    flags = _flag_transform(flags)
    return _wcparse.translate(patterns, flags, limit, exclude=exclude)


def fnmatch(
    filename: AnyStr,
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> bool:
    """
    Check if filename matches pattern.

    By default case sensitivity is determined by the file system,
    but if `case_sensitive` is set, respect that instead.
    """

    flags = _flag_transform(flags)
    return bool(_wcparse.compile(patterns, flags, limit, exclude=exclude).match(filename))


def filter(  # noqa A001
    filenames: Iterable[AnyStr],
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> list[AnyStr]:
    """Filter names using pattern."""

    matches = []

    flags = _flag_transform(flags)
    obj = _wcparse.compile(patterns, flags, limit, exclude=exclude)

    for filename in filenames:
        if obj.match(filename):
            matches.append(filename)  # noqa: PERF401
    return matches


def escape(pattern: AnyStr) -> AnyStr:
    """Escape."""

    return _wcparse.escape(pattern, pathname=False)


def is_magic(pattern: AnyStr, *, flags: int = 0) -> bool:
    """Check if the pattern is likely to be magic."""

    flags = _flag_transform(flags)
    return _wcparse.is_magic(pattern, flags)
