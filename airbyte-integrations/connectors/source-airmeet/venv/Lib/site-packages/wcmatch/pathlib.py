"""Pathlib implementation that uses our own glob."""
from __future__ import annotations
import pathlib
import os
from . import glob
from . import _wcparse
from . import util
from typing import Iterable, Any, Sequence

__all__ = (
    "CASE", "IGNORECASE", "RAWCHARS", "DOTGLOB", "DOTMATCH",
    "EXTGLOB", "EXTMATCH", "NEGATE", "MINUSNEGATE", "BRACE",
    "REALPATH", "FOLLOW", "MATCHBASE", "NEGATEALL", "NODIR", "NOUNIQUE",
    "NODOTDIR", "SCANDOTDIR", "GLOBSTARLONG",
    "C", "I", "R", "D", "E", "G", "N", "B", "M", "P", "L", "S", "X", "O", "A", "Q", "Z", "SD", "GL",
    "Path", "PurePath", "WindowsPath", "PosixPath", "PurePosixPath", "PureWindowsPath"
)

C = CASE = glob.CASE
I = IGNORECASE = glob.IGNORECASE
R = RAWCHARS = glob.RAWCHARS
D = DOTGLOB = DOTMATCH = glob.DOTMATCH
E = EXTGLOB = EXTMATCH = glob.EXTMATCH
G = GLOBSTAR = glob.GLOBSTAR
N = NEGATE = glob.NEGATE
B = BRACE = glob.BRACE
M = MINUSNEGATE = glob.MINUSNEGATE
P = REALPATH = glob.REALPATH
L = FOLLOW = glob.FOLLOW
S = SPLIT = glob.SPLIT
X = MATCHBASE = glob.MATCHBASE
O = NODIR = glob.NODIR
A = NEGATEALL = glob.NEGATEALL
Q = NOUNIQUE = glob.NOUNIQUE
Z = NODOTDIR = glob.NODOTDIR
GL = GLOBSTARLONG = glob.GLOBSTARLONG

SD = SCANDOTDIR = glob.SCANDOTDIR

# Internal flags
_EXTMATCHBASE = _wcparse._EXTMATCHBASE
_NOABSOLUTE = _wcparse._NOABSOLUTE
_PATHNAME = _wcparse.PATHNAME
_FORCEWIN = _wcparse.FORCEWIN
_FORCEUNIX = _wcparse.FORCEUNIX

_PATHLIB = glob._PATHLIB

FLAG_MASK = (
    CASE |
    IGNORECASE |
    RAWCHARS |
    DOTMATCH |
    EXTMATCH |
    GLOBSTAR |
    GLOBSTARLONG |
    NEGATE |
    MINUSNEGATE |
    BRACE |
    REALPATH |
    FOLLOW |
    SPLIT |
    MATCHBASE |
    NODIR |
    NEGATEALL |
    NOUNIQUE |
    NODOTDIR |
    _EXTMATCHBASE |
    _NOABSOLUTE
)


class PurePath(pathlib.PurePath):
    """Special pure pathlike object that uses our own glob methods."""

    __slots__ = ()

    def __new__(cls, *args: str) -> 'PurePath':
        """New."""

        if cls is PurePath:
            cls = PureWindowsPath if os.name == 'nt' else PurePosixPath
        if not util.PY312:
            return cls._from_parts(args)  # type: ignore[no-any-return,attr-defined]
        else:
            return object.__new__(cls)

    def _translate_flags(self, flags: int) -> int:
        """Translate flags for the current `pathlib` object."""

        flags = (flags & FLAG_MASK) | _PATHNAME
        if flags & REALPATH:
            flags |= _FORCEWIN if os.name == 'nt' else _FORCEUNIX
        if isinstance(self, PureWindowsPath):
            if flags & _FORCEUNIX:
                raise ValueError("Windows pathlike objects cannot be forced to behave like a Posix path")
            flags |= _FORCEWIN
        elif isinstance(self, PurePosixPath):
            if flags & _FORCEWIN:
                raise ValueError("Posix pathlike objects cannot be forced to behave like a Windows path")
            flags |= _FORCEUNIX
        return flags

    def _translate_path(self) -> str:
        """Translate the object to a path string and ensure trailing slash for non-pure paths that are directories."""

        sep = ''
        name = str(self)
        if isinstance(self, Path) and name and self.is_dir():
            sep = self.parser.sep if util.PY313 else self._flavour.sep

        return name + sep

    def match(  # type: ignore[override, unused-ignore]
        self,
        patterns: str | Sequence[str],
        *,
        flags: int = 0,
        limit: int = _wcparse.PATTERN_LIMIT,
        exclude: str | Sequence[str] | None = None
    ) -> bool:
        """
        Match patterns using `globmatch`, but also using the same right to left logic that the default `pathlib` uses.

        This uses the same right to left logic that the default `pathlib` object uses.
        Folders and files are essentially matched from right to left.
        """

        return self.globmatch(patterns, flags=flags | _EXTMATCHBASE, limit=limit, exclude=exclude)

    def globmatch(
        self,
        patterns: str | Sequence[str],
        *,
        flags: int = 0,
        limit: int = _wcparse.PATTERN_LIMIT,
        exclude: str | Sequence[str] | None = None
    ) -> bool:
        """Match patterns using `globmatch`, but without the right to left logic that the default `pathlib` uses."""

        return glob.globmatch(
            self._translate_path(),
            patterns,
            flags=self._translate_flags(flags),
            limit=limit,
            exclude=exclude
        )

    def full_match(  # type: ignore[override, unused-ignore]
        self,
        patterns: str | Sequence[str],
        *,
        flags: int = 0,
        limit: int = _wcparse.PATTERN_LIMIT,
        exclude: str | Sequence[str] | None = None
    ) -> bool:
        """Alias for Python 3.13 `full_match`, but redirects to use `globmatch`."""

        return glob.globmatch(
            self._translate_path(),
            patterns,
            flags=self._translate_flags(flags),
            limit=limit,
            exclude=exclude
        )


class Path(pathlib.Path):
    """Special pathlike object (which accesses the filesystem) that uses our own glob methods."""

    __slots__ = ()

    def __new__(cls, *args: str, **kwargs: Any) -> 'Path':
        """New."""

        win_host = os.name == 'nt'
        if cls is Path:
            cls = WindowsPath if win_host else PosixPath
        if not util.PY312:
            if util.PY310:
                self = cls._from_parts(args)  # type: ignore[attr-defined]
            else:
                self = cls._from_parts(args, init=False)  # type: ignore[attr-defined]
            if not self._flavour.is_supported:
                raise NotImplementedError(f"Cannot instantiate {cls.__name__!r} on your system")
            if not util.PY310:
                self._init()
            return self  # type: ignore[no-any-return]
        else:
            if cls is WindowsPath and not win_host or cls is not WindowsPath and win_host:
                raise NotImplementedError(f"Cannot instantiate {cls.__name__!r} on your system")
            return object.__new__(cls)

    def glob(  # type: ignore[override]
        self,
        patterns: str | Sequence[str],
        *,
        flags: int = 0,
        limit: int = _wcparse.PATTERN_LIMIT,
        exclude: str | Sequence[str] | None = None
    ) -> Iterable['Path']:
        """
        Search the file system.

        `GLOBSTAR` is enabled by default in order match the default behavior of `pathlib`.

        """

        if self.is_dir():
            scandotdir = flags & SCANDOTDIR
            flags = self._translate_flags(  # type: ignore[attr-defined]
                flags | _NOABSOLUTE
            ) | ((_PATHLIB | SCANDOTDIR) if scandotdir else _PATHLIB)
            for filename in glob.iglob(patterns, flags=flags, root_dir=str(self), limit=limit, exclude=exclude):
                yield self.joinpath(filename)

    def rglob(  # type: ignore[override]
        self,
        patterns: str | Sequence[str],
        *,
        flags: int = 0,
        limit: int = _wcparse.PATTERN_LIMIT,
        exclude: str | Sequence[str] | None = None
    ) -> Iterable['Path']:
        """
        Recursive glob.

        This uses the same recursive logic that the default `pathlib` object uses.
        Folders and files are essentially matched from right to left.

        `GLOBSTAR` is enabled by default in order match the default behavior of `pathlib`.

        """

        yield from self.glob(patterns, flags=flags | _EXTMATCHBASE, limit=limit, exclude=exclude)


class PurePosixPath(PurePath, pathlib.PurePosixPath):
    """Pure Posix path."""

    __slots__ = ()


class PureWindowsPath(PurePath, pathlib.PureWindowsPath):
    """Pure Windows path."""

    __slots__ = ()


class PosixPath(Path, PurePosixPath):
    """Posix path."""

    __slots__ = ()


class WindowsPath(Path, PureWindowsPath):
    """Windows path."""

    __slots__ = ()
