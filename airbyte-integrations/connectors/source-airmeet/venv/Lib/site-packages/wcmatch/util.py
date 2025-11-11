"""Compatibility module."""
from __future__ import annotations
import sys
import os
import stat
import re
import unicodedata
from functools import wraps
import warnings
from typing import Any, Callable, AnyStr, Match, Pattern

PY310 = (3, 10) <= sys.version_info
PY312 = (3, 12) <= sys.version_info
PY313 = (3, 13) <= sys.version_info

UNICODE = 0
BYTES = 1

CASE_FS = os.path.normcase('A') != os.path.normcase('a')

RE_NORM = re.compile(
    r'''(?x)
    (/|\\/)|
    (\\[abfnrtv\\])|
    (\\(?:U[\da-fA-F]{8}|u[\da-fA-F]{4}|x[\da-fA-F]{2}|([0-7]{1,3})))|
    (\\N\{[^}]*?\})|
    (\\[^NUux]) |
    (\\[NUux])
    '''
)

RE_BNORM = re.compile(
    br'''(?x)
    (/|\\/)|
    (\\[abfnrtv\\])|
    (\\(?:x[\da-fA-F]{2}|([0-7]{1,3})))|
    (\\[^x]) |
    (\\[x])
    '''
)

BACK_SLASH_TRANSLATION = {
    r"\a": '\a',
    r"\b": '\b',
    r"\f": '\f',
    r"\r": '\r',
    r"\t": '\t',
    r"\n": '\n',
    r"\v": '\v',
    r"\\": r'\\',
    br"\a": b'\a',
    br"\b": b'\b',
    br"\f": b'\f',
    br"\r": b'\r',
    br"\t": b'\t',
    br"\n": b'\n',
    br"\v": b'\v',
    br"\\": br'\\'
}

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":  # pragma: no cover
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def platform() -> str:
    """Get platform."""

    return _PLATFORM


def is_case_sensitive() -> bool:
    """Check if case sensitive."""

    return CASE_FS


def norm_pattern(pattern: AnyStr, normalize: bool | None, is_raw_chars: bool) -> AnyStr:
    r"""
    Normalize pattern.

    - For windows systems we want to normalize slashes to \.
    - If raw string chars is enabled, we want to also convert
      encoded string chars to literal characters.
    - If `normalize` is enabled, take care to convert \/ to \\\\.
    """

    if isinstance(pattern, bytes):
        is_bytes = True
        slash = b'\\'
        multi_slash = slash * 4
        pat = RE_BNORM
    else:
        is_bytes = False
        slash = '\\'
        multi_slash = slash * 4
        pat = RE_NORM

    if not normalize and not is_raw_chars:
        return pattern

    def norm(m: Match[AnyStr]) -> AnyStr:
        """Normalize the pattern."""

        if m.group(1):
            char = m.group(1)
            if normalize and len(char) > 1:
                char = multi_slash
        elif m.group(2):
            char = BACK_SLASH_TRANSLATION[m.group(2)] if is_raw_chars else m.group(2)
        elif is_raw_chars and m.group(4):
            char = bytes([int(m.group(4), 8) & 0xFF]) if is_bytes else chr(int(m.group(4), 8))
        elif is_raw_chars and m.group(3):
            char = bytes([int(m.group(3)[2:], 16)]) if is_bytes else chr(int(m.group(3)[2:], 16))
        elif is_raw_chars and not is_bytes and m.group(5):
            char = unicodedata.lookup(m.group(5)[3:-1])
        elif not is_raw_chars or m.group(5 if is_bytes else 6):
            char = m.group(0)
        else:
            value = m.group(6) if is_bytes else m.group(7)
            pos = m.start(6) if is_bytes else m.start(7)
            raise SyntaxError(f"Could not convert character value {value!r} at position {pos:d}")
        return char

    return pat.sub(norm, pattern)


class StringIter:
    """Preprocess replace tokens."""

    def __init__(self, string: str) -> None:
        """Initialize."""

        self._string = string
        self._index = 0

    def __iter__(self) -> "StringIter":
        """Iterate."""

        return self

    def __next__(self) -> str:
        """Python 3 iterator compatible next."""

        return self.iternext()

    def match(self, pattern: Pattern[str]) -> Match[str] | None:
        """Perform regex match at index."""

        m = pattern.match(self._string, self._index)
        if m:
            self._index = m.end()
        return m

    @property
    def index(self) -> int:
        """Get current index."""

        return self._index

    def previous(self) -> str:  # pragma: no cover
        """Get previous char."""

        return self._string[self._index - 1]

    def advance(self, count: int) -> None:  # pragma: no cover
        """Advanced the index."""

        self._index += count

    def rewind(self, count: int) -> None:
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self) -> str:
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError as e:  # pragma: no cover
            raise StopIteration from e

        return char


class Immutable:
    """Immutable."""

    __slots__: tuple[Any, ...] = ()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize."""

        for k, v in kwargs.items():
            super(Immutable, self).__setattr__(k, v)

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover
        """Prevent mutability."""

        raise AttributeError('Class is immutable!')


def is_hidden(path: AnyStr) -> bool:
    """Check if file is hidden."""

    hidden = False
    f = os.path.basename(path)
    if f[:1] in ('.', b'.'):
        # Count dot file as hidden on all systems
        hidden = True
    elif sys.platform == 'win32':
        # On Windows, look for `FILE_ATTRIBUTE_HIDDEN`
        results = os.lstat(path)
        FILE_ATTRIBUTE_HIDDEN = 0x2
        hidden = bool(results.st_file_attributes & FILE_ATTRIBUTE_HIDDEN)
    elif sys.platform == "darwin":  # pragma: no cover
        # On macOS, look for `UF_HIDDEN`
        results = os.lstat(path)
        hidden = bool(results.st_flags & stat.UF_HIDDEN)
    return hidden


def deprecated(message: str, stacklevel: int = 2) -> Callable[..., Any]:  # pragma: no cover
    """
    Raise a `DeprecationWarning` when wrapped function/method is called.

    Usage:

        @deprecated("This method will be removed in version X; use Y instead.")
        def some_method()"
            pass
    """

    def _wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def _deprecated_func(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"'{func.__name__}' is deprecated. {message}",
                category=DeprecationWarning,
                stacklevel=stacklevel
            )
            return func(*args, **kwargs)
        return _deprecated_func
    return _wrapper


def warn_deprecated(message: str, stacklevel: int = 2) -> None:  # pragma: no cover
    """Warn deprecated."""

    warnings.warn(
        message,
        category=DeprecationWarning,
        stacklevel=stacklevel
    )
