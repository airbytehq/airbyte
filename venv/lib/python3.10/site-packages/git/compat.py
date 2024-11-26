# Copyright (C) 2008, 2009 Michael Trier (mtrier@gmail.com) and contributors
#
# This module is part of GitPython and is released under the
# 3-Clause BSD License: https://opensource.org/license/bsd-3-clause/

"""Utilities to help provide compatibility with Python 3."""

import locale
import os
import sys

from gitdb.utils.encoding import force_bytes, force_text  # noqa: F401  # @UnusedImport

# typing --------------------------------------------------------------------

from typing import (  # noqa: F401
    Any,
    AnyStr,
    Dict,
    IO,
    Optional,
    Tuple,
    Type,
    Union,
    overload,
)

# ---------------------------------------------------------------------------


is_win = os.name == "nt"
"""Deprecated alias for ``os.name == "nt"`` to check for native Windows.

This is deprecated because it is clearer to write out :attr:`os.name` or
:attr:`sys.platform` checks explicitly, especially in cases where it matters which is
used.

:note: ``is_win`` is ``False`` on Cygwin, but is often wrongly assumed ``True``. To
    detect Cygwin, use ``sys.platform == "cygwin"``.
"""

is_posix = os.name == "posix"
"""Deprecated alias for ``os.name == "posix"`` to check for Unix-like ("POSIX") systems.

This is deprecated because it clearer to write out :attr:`os.name` or
:attr:`sys.platform` checks explicitly, especially in cases where it matters which is
used.

:note: For POSIX systems, more detailed information is available in
    :attr:`sys.platform`, while :attr:`os.name` is always ``"posix"`` on such systems,
    including macOS (Darwin).
"""

is_darwin = sys.platform == "darwin"
"""Deprecated alias for ``sys.platform == "darwin"`` to check for macOS (Darwin).

This is deprecated because it clearer to write out :attr:`os.name` or
:attr:`sys.platform` checks explicitly.

:note: For macOS (Darwin), ``os.name == "posix"`` as in other Unix-like systems, while
    ``sys.platform == "darwin"`.
"""

defenc = sys.getfilesystemencoding()
"""The encoding used to convert between Unicode and bytes filenames."""


@overload
def safe_decode(s: None) -> None:
    ...


@overload
def safe_decode(s: AnyStr) -> str:
    ...


def safe_decode(s: Union[AnyStr, None]) -> Optional[str]:
    """Safely decode a binary string to Unicode."""
    if isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return s.decode(defenc, "surrogateescape")
    elif s is None:
        return None
    else:
        raise TypeError("Expected bytes or text, but got %r" % (s,))


@overload
def safe_encode(s: None) -> None:
    ...


@overload
def safe_encode(s: AnyStr) -> bytes:
    ...


def safe_encode(s: Optional[AnyStr]) -> Optional[bytes]:
    """Safely encode a binary string to Unicode."""
    if isinstance(s, str):
        return s.encode(defenc)
    elif isinstance(s, bytes):
        return s
    elif s is None:
        return None
    else:
        raise TypeError("Expected bytes or text, but got %r" % (s,))


@overload
def win_encode(s: None) -> None:
    ...


@overload
def win_encode(s: AnyStr) -> bytes:
    ...


def win_encode(s: Optional[AnyStr]) -> Optional[bytes]:
    """Encode Unicode strings for process arguments on Windows."""
    if isinstance(s, str):
        return s.encode(locale.getpreferredencoding(False))
    elif isinstance(s, bytes):
        return s
    elif s is not None:
        raise TypeError("Expected bytes or text, but got %r" % (s,))
    return None
