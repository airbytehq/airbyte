"""
Wild Card Match.

A module for performing wild card matches.
"""
from __future__ import annotations
import os
import re
from . import _wcparse
from . import _wcmatch
from . import util
from typing import Any, Iterator, Generic, AnyStr


__all__ = (
    "CASE", "IGNORECASE", "RAWCHARS", "FILEPATHNAME", "DIRPATHNAME", "PATHNAME",
    "EXTMATCH", "GLOBSTAR", "BRACE", "MINUSNEGATE", "SYMLINKS", "HIDDEN", "RECURSIVE",
    "MATCHBASE",
    "C", "I", "R", "P", "E", "G", "M", "DP", "FP", "SL", "HD", "RV", "X", "B",
    "WcMatch"
)

C = CASE = _wcparse.CASE
I = IGNORECASE = _wcparse.IGNORECASE
R = RAWCHARS = _wcparse.RAWCHARS
E = EXTMATCH = _wcparse.EXTMATCH
G = GLOBSTAR = _wcparse.GLOBSTAR
B = BRACE = _wcparse.BRACE
M = MINUSNEGATE = _wcparse.MINUSNEGATE
X = MATCHBASE = _wcparse.MATCHBASE

# Control `PATHNAME` individually for folder exclude and files
DP = DIRPATHNAME = 0x1000000
FP = FILEPATHNAME = 0x2000000
SL = SYMLINKS = 0x4000000
HD = HIDDEN = 0x8000000
RV = RECURSIVE = 0x10000000

# Internal flags
_ANCHOR = _wcparse._ANCHOR
_NEGATE = _wcparse.NEGATE
_DOTMATCH = _wcparse.DOTMATCH
_NEGATEALL = _wcparse.NEGATEALL
_SPLIT = _wcparse.SPLIT
_FORCEWIN = _wcparse.FORCEWIN
_PATHNAME = _wcparse.PATHNAME

# Control `PATHNAME` for file and folder
P = PATHNAME = DIRPATHNAME | FILEPATHNAME

FLAG_MASK = (
    CASE |
    IGNORECASE |
    RAWCHARS |
    EXTMATCH |
    GLOBSTAR |
    BRACE |
    MINUSNEGATE |
    DIRPATHNAME |
    FILEPATHNAME |
    SYMLINKS |
    HIDDEN |
    RECURSIVE |
    MATCHBASE
)


class WcMatch(Generic[AnyStr]):
    """Finds files by wildcard."""

    def __init__(
        self,
        root_dir: AnyStr,
        file_pattern: AnyStr | None = None,
        exclude_pattern: AnyStr | None = None,
        flags: int = 0,
        limit: int = _wcparse.PATHNAME,
        **kwargs: Any
    ):
        """Initialize the directory walker object."""

        self.is_bytes = isinstance(root_dir, bytes)
        self._directory = self._norm_slash(root_dir)  # type: AnyStr
        self._abort = False
        self._skipped = 0
        self._parse_flags(flags)
        self._sep = os.fsencode(os.sep) if isinstance(root_dir, bytes) else os.sep  # type: AnyStr
        self._root_dir = self._add_sep(self._get_cwd(), True)  # type: AnyStr
        self.limit = limit
        empty = os.fsencode('') if isinstance(root_dir, bytes) else ''
        self.pattern_file = file_pattern if file_pattern is not None else empty  # type: AnyStr
        self.pattern_folder_exclude = exclude_pattern if exclude_pattern is not None else empty  # type: AnyStr
        self.file_check = None  # type: _wcmatch.WcRegexp[AnyStr] | None
        self.folder_exclude_check = None  # type: _wcmatch.WcRegexp[AnyStr] | None
        self.on_init(**kwargs)
        self._compile(self.pattern_file, self.pattern_folder_exclude)

    def _norm_slash(self, name: AnyStr) -> AnyStr:
        """Normalize path slashes."""

        if util.is_case_sensitive():
            return name
        elif isinstance(name, bytes):
            return name.replace(b'/', b"\\")
        else:
            return name.replace('/', "\\")

    def _add_sep(self, path: AnyStr, check: bool = False) -> AnyStr:
        """Add separator."""

        return (path + self._sep) if not check or not path.endswith(self._sep) else path

    def _get_cwd(self) -> AnyStr:
        """Get current working directory."""

        if self._directory:
            return self._directory
        elif isinstance(self._directory, bytes):
            return bytes(os.curdir, 'ASCII')
        else:
            return os.curdir

    def _parse_flags(self, flags: int) -> None:
        """Parse flags."""

        self.flags = flags & FLAG_MASK
        self.flags |= _NEGATE | _DOTMATCH | _NEGATEALL | _SPLIT
        self.follow_links = bool(self.flags & SYMLINKS)
        self.show_hidden = bool(self.flags & HIDDEN)
        self.recursive = bool(self.flags & RECURSIVE)
        self.dir_pathname = bool(self.flags & DIRPATHNAME)
        self.file_pathname = bool(self.flags & FILEPATHNAME)
        self.matchbase = bool(self.flags & MATCHBASE)
        if util.platform() == "windows":
            self.flags |= _FORCEWIN
        self.flags = self.flags & (_wcparse.FLAG_MASK ^ MATCHBASE)

    def _compile_wildcard(self, pattern: AnyStr, pathname: bool = False) -> _wcmatch.WcRegexp[AnyStr] | None:
        """Compile or format the wildcard inclusion/exclusion pattern."""

        flags = self.flags
        if pathname:
            flags |= _PATHNAME | _ANCHOR
            if self.matchbase:
                flags |= MATCHBASE

        return _wcparse.compile([pattern], flags, self.limit) if pattern else None

    def _compile(self, file_pattern: AnyStr, folder_exclude_pattern: AnyStr) -> None:
        """Compile patterns."""

        if self.file_check is None:
            if not file_pattern:
                self.file_check = _wcmatch.WcRegexp(
                    (re.compile(br'^.*$' if isinstance(file_pattern, bytes) else r'^.*$', re.DOTALL),)
                )
            else:
                self.file_check = self._compile_wildcard(file_pattern, self.file_pathname)

        if self.folder_exclude_check is None:
            if not folder_exclude_pattern:
                self.folder_exclude_check = _wcmatch.WcRegexp(())
            else:
                self.folder_exclude_check = self._compile_wildcard(folder_exclude_pattern, self.dir_pathname)

    def _valid_file(self, base: AnyStr, name: AnyStr) -> bool:
        """Return whether a file can be searched."""

        valid = False
        fullpath = os.path.join(base, name)
        if self.file_check is not None and self.compare_file(fullpath[self._base_len:] if self.file_pathname else name):
            valid = True
        if valid and (not self.show_hidden and util.is_hidden(fullpath)):
            valid = False
        return self.on_validate_file(base, name) if valid else valid

    def compare_file(self, filename: AnyStr) -> bool:
        """Compare filename."""

        return self.file_check.match(filename)  # type: ignore[union-attr]

    def on_validate_file(self, base: AnyStr, name: AnyStr) -> bool:
        """Validate file override."""

        return True

    def _valid_folder(self, base: AnyStr, name: AnyStr) -> bool:
        """Return whether a folder can be searched."""

        valid = True
        fullpath = os.path.join(base, name)
        if (
            not self.recursive or
            (
                self.folder_exclude_check and
                not self.compare_directory(fullpath[self._base_len:] if self.dir_pathname else name)
            )
        ):
            valid = False
        if valid and (not self.show_hidden and util.is_hidden(fullpath)):
            valid = False
        return self.on_validate_directory(base, name) if valid else valid

    def compare_directory(self, directory: AnyStr) -> bool:
        """Compare folder."""

        return not self.folder_exclude_check.match(  # type: ignore[union-attr]
            self._add_sep(directory) if self.dir_pathname else directory
        )

    def on_init(self, **kwargs: Any) -> None:
        """Handle custom initialization."""

    def on_validate_directory(self, base: AnyStr, name: AnyStr) -> bool:
        """Validate folder override."""

        return True

    def on_skip(self, base: AnyStr, name: AnyStr) -> Any:
        """On skip."""

        return None

    def on_error(self, base: AnyStr, name: AnyStr) -> Any:
        """On error."""

        return None

    def on_match(self, base: AnyStr, name: AnyStr) -> Any:
        """On match."""

        return os.path.join(base, name)

    def on_reset(self) -> None:
        """On reset."""

    def get_skipped(self) -> int:
        """Get number of skipped files."""

        return self._skipped

    def kill(self) -> None:
        """Abort process."""

        self._abort = True

    def is_aborted(self) -> bool:
        """Check if process has been aborted."""

        return self._abort

    def reset(self) -> None:
        """Revive class from a killed state."""

        self._abort = False

    def _walk(self) -> Iterator[Any]:
        """Start search for valid files."""

        self._base_len = len(self._root_dir)

        for base, dirs, files in os.walk(self._root_dir, followlinks=self.follow_links):
            if self.is_aborted():
                break

            # Remove child folders based on exclude rules
            for name in dirs[:]:
                try:
                    if not self._valid_folder(base, name):
                        dirs.remove(name)
                except Exception:
                    dirs.remove(name)
                    value = self.on_error(base, name)
                    if value is not None:  # pragma: no cover
                        yield value

                if self.is_aborted():  # pragma: no cover
                    break

            # Search files if they were found
            if files:
                # Only search files that are in the include rules
                for name in files:
                    try:
                        valid = self._valid_file(base, name)
                    except Exception:
                        valid = False
                        value = self.on_error(base, name)
                        if value is not None:
                            yield value

                    if valid:
                        yield self.on_match(base, name)
                    else:
                        self._skipped += 1
                        value = self.on_skip(base, name)
                        if value is not None:
                            yield value

                    if self.is_aborted():
                        break

    def match(self) -> list[Any]:
        """Run the directory walker."""

        return list(self.imatch())

    def imatch(self) -> Iterator[Any]:
        """Run the directory walker as iterator."""

        self.on_reset()
        self._skipped = 0
        for f in self._walk():
            yield f
