"""
Wild Card Match.

A custom implementation of `glob`.
"""
from __future__ import annotations
import os
import sys
import re
import functools
from collections import namedtuple
import bracex
from . import _wcparse
from . import _wcmatch
from . import util
from typing import Iterator, Iterable, AnyStr, Generic, Pattern, Callable, Any, Sequence

__all__ = (
    "CASE", "IGNORECASE", "RAWCHARS", "DOTGLOB", "DOTMATCH",
    "EXTGLOB", "EXTMATCH", "GLOBSTAR", "NEGATE", "MINUSNEGATE", "BRACE", "NOUNIQUE",
    "REALPATH", "FOLLOW", "MATCHBASE", "MARK", "NEGATEALL", "NODIR", "FORCEWIN", "FORCEUNIX", "GLOBTILDE",
    "NODOTDIR", "SCANDOTDIR", "SUPPORT_DIR_FD", "GLOBSTARLONG",
    "C", "I", "R", "D", "E", "G", "N", "M", "B", "P", "L", "S", "X", 'K', "O", "A", "W", "U", "T", "Q", "Z", "SD", "GL",
    "iglob", "glob", "globmatch", "globfilter", "escape", "is_magic"
)

# We don't use `util.platform` only because we mock it in tests,
# and `scandir` will not work with bytes on the wrong system.
WIN = sys.platform.startswith('win')

SUPPORT_DIR_FD = _wcmatch.SUPPORT_DIR_FD

C = CASE = _wcparse.CASE
I = IGNORECASE = _wcparse.IGNORECASE
R = RAWCHARS = _wcparse.RAWCHARS
D = DOTGLOB = DOTMATCH = _wcparse.DOTMATCH
E = EXTGLOB = EXTMATCH = _wcparse.EXTMATCH
G = GLOBSTAR = _wcparse.GLOBSTAR
N = NEGATE = _wcparse.NEGATE
M = MINUSNEGATE = _wcparse.MINUSNEGATE
B = BRACE = _wcparse.BRACE
P = REALPATH = _wcparse.REALPATH
L = FOLLOW = _wcparse.FOLLOW
S = SPLIT = _wcparse.SPLIT
X = MATCHBASE = _wcparse.MATCHBASE
O = NODIR = _wcparse.NODIR
A = NEGATEALL = _wcparse.NEGATEALL
W = FORCEWIN = _wcparse.FORCEWIN
U = FORCEUNIX = _wcparse.FORCEUNIX
T = GLOBTILDE = _wcparse.GLOBTILDE
Q = NOUNIQUE = _wcparse.NOUNIQUE
Z = NODOTDIR = _wcparse.NODOTDIR
GL = GLOBSTARLONG = _wcparse.GLOBSTARLONG

K = MARK = 0x1000000
SD = SCANDOTDIR = 0x2000000

_PATHLIB = 0x8000000

# Internal flags
_EXTMATCHBASE = _wcparse._EXTMATCHBASE
_NOABSOLUTE = _wcparse._NOABSOLUTE
_PATHNAME = _wcparse.PATHNAME

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
    FORCEWIN |
    FORCEUNIX |
    GLOBTILDE |
    NOUNIQUE |
    NODOTDIR |
    _EXTMATCHBASE |
    _NOABSOLUTE
)

_RE_PATHLIB_DOT_NORM = (
    re.compile(r'(?:((?<=^)|(?<=/))\.(?:/|$))+'),
    re.compile(br'(?:((?<=^)|(?<=/))\.(?:/|$))+')
)  # type: tuple[Pattern[str], Pattern[bytes]]

_RE_WIN_PATHLIB_DOT_NORM = (
    re.compile(r'(?:((?<=^)|(?<=[\\/]))\.(?:[\\/]|$))+'),
    re.compile(br'(?:((?<=^)|(?<=[\\/]))\.(?:[\\/]|$))+')
)  # type: tuple[Pattern[str], Pattern[bytes]]


def _flag_transform(flags: int) -> int:
    """Transform flags to glob defaults."""

    # Enabling both cancels out
    if flags & FORCEUNIX and flags & FORCEWIN:
        flags ^= FORCEWIN | FORCEUNIX

    # Here we force `PATHNAME`.
    flags = (flags & FLAG_MASK) | _PATHNAME
    if flags & REALPATH:
        if util.platform() == "windows":
            if flags & FORCEUNIX:
                flags ^= FORCEUNIX
            flags |= FORCEWIN
        else:
            if flags & FORCEWIN:
                flags ^= FORCEWIN

    return flags


class _GlobPart(
    namedtuple('_GlobPart', ['pattern', 'is_magic', 'is_globstar', 'is_globstarlong', 'dir_only', 'is_drive']),
):
    """File Glob."""


class _GlobSplit(Generic[AnyStr]):
    """
    Split glob pattern on "magic" file and directories.

    Glob pattern return a list of patterns broken down at the directory
    boundary. Each piece will either be a literal file part or a magic part.
    Each part will will contain info regarding whether they are
    a directory pattern or a file pattern and whether the part
    is "magic", etc.: `["pattern", is_magic, is_globstar, dir_only, is_drive]`.

    Example:
    -------
        `"**/this/is_literal/*magic?/@(magic|part)"`

        Would  become:

        ```
        [
            ["**", True, True, False, False],
            ["this", False, False, True, False],
            ["is_literal", False, False, True, False],
            ["*magic?", True, False, True, False],
            ["@(magic|part)", True, False, False, False]
        ]
        ```

    """

    def __init__(self, pattern: AnyStr, flags: int) -> None:
        """Initialize."""

        self.pattern = pattern  # type: AnyStr
        self.unix = _wcparse.is_unix_style(flags)
        self.flags = flags
        self.no_abs = bool(flags & _wcparse._NOABSOLUTE)
        self.globstarlong = bool(flags & GLOBSTARLONG)
        self.globstar = self.globstarlong or bool(flags & GLOBSTAR)
        self.follow = bool(flags & FOLLOW)
        self.matchbase = bool(flags & MATCHBASE)
        self.extmatchbase = bool(flags & _wcparse._EXTMATCHBASE)
        self.tilde = bool(flags & GLOBTILDE)
        if _wcparse.is_negative(self.pattern, flags):  # pragma: no cover
            # This isn't really used, but we'll keep it around
            # in case we find a reason to directly send inverse patterns
            # Through here.
            self.pattern = self.pattern[0:1]
        if flags & NEGATE:
            flags ^= NEGATE
        self.flags = flags
        self.extend = bool(flags & EXTMATCH)
        if not self.unix:
            self.win_drive_detect = True
            self.bslash_abort = True
            self.sep = '\\'
        else:
            self.win_drive_detect = False
            self.bslash_abort = False
            self.sep = '/'
        # Once split, Windows file names will never have `\\` in them,
        # so we can use the Unix magic detect
        self.magic_symbols = _wcparse._get_magic_symbols(pattern, self.unix, self.flags)[0]  # type: set[AnyStr]

    def is_magic(self, name: AnyStr) -> bool:
        """Check if name contains magic characters."""

        for c in self.magic_symbols:
            if c in name:
                return True
        return False

    def _sequence(self, i: util.StringIter) -> None:
        """Handle character group."""

        c = next(i)
        if c == '!':
            c = next(i)
        if c in ('^', '-', '['):
            c = next(i)

        while c != ']':
            if c == '\\':
                # Handle escapes
                try:
                    self._references(i, True)
                except _wcparse.PathNameException as e:
                    raise StopIteration from e
            elif c == '/':
                raise StopIteration
            c = next(i)

    def _references(self, i: util.StringIter, sequence: bool = False) -> str:
        """Handle references."""

        value = ''

        c = next(i)
        if c == '\\':
            # \\
            if sequence and self.bslash_abort:
                raise _wcparse.PathNameException
            value = c
        elif c == '/':
            # \/
            if sequence:
                raise _wcparse.PathNameException
            value = c
        else:
            # \a, \b, \c, etc.
            pass
        return value

    def parse_extend(self, c: str, i: util.StringIter) -> bool:
        """Parse extended pattern lists."""

        # Start list parsing
        success = True
        index = i.index
        list_type = c
        try:
            c = next(i)
            if c != '(':
                raise StopIteration
            while c != ')':
                c = next(i)

                if self.extend and c in _wcparse.EXT_TYPES and self.parse_extend(c, i):
                    continue

                if c == '\\':
                    try:
                        self._references(i)
                    except StopIteration:
                        pass
                elif c == '[':
                    index = i.index
                    try:
                        self._sequence(i)
                    except StopIteration:
                        i.rewind(i.index - index)

        except StopIteration:
            success = False
            c = list_type
            i.rewind(i.index - index)

        return success

    def store(self, value: AnyStr, l: list[_GlobPart], dir_only: bool) -> None:
        """Group patterns by literals and potential magic patterns."""

        if l and value in (b'', ''):
            return

        globstarlong = self.globstarlong and value in (b'***', '***')
        globstar = globstarlong or (self.globstar and value in (b'**', '**'))
        magic = self.is_magic(value)
        if magic:
            v = _wcparse._compile(value, self.flags)  # type: Pattern[AnyStr] | AnyStr
        else:
            v = value
        if globstar and l and l[-1].is_globstar:
            l[-1] = _GlobPart(v, magic, globstar, globstarlong, dir_only, False)
        else:
            l.append(_GlobPart(v, magic, globstar, globstarlong, dir_only, False))

    def split(self) -> list[_GlobPart]:
        """Start parsing the pattern."""

        split_index = []
        parts = []
        start = -1

        if isinstance(self.pattern, bytes):
            is_bytes = True
            pattern = self.pattern.decode('latin-1')
        else:
            is_bytes = False
            pattern = self.pattern

        i = util.StringIter(pattern)

        # Detect and store away windows drive as a literal
        if self.win_drive_detect:
            root_specified, drive, slash, end = _wcparse._get_win_drive(pattern)
            if drive is not None:
                parts.append(_GlobPart(drive.encode('latin-1') if is_bytes else drive, False, False, False, True, True))
                start = end - 1
                i.advance(start)
            elif drive is None and root_specified:
                parts.append(_GlobPart(b'\\' if is_bytes else '\\', False, False, False, True, True))
                if pattern.startswith('/'):
                    start = 0
                    i.advance(1)
                else:
                    start = 1
                    i.advance(2)
        elif not self.win_drive_detect and pattern.startswith('/'):
            parts.append(_GlobPart(b'/' if is_bytes else '/', False, False, False, True, True))
            start = 0
            i.advance(1)

        for c in i:
            if self.extend and c in _wcparse.EXT_TYPES and self.parse_extend(c, i):
                continue

            if c == '\\':
                index = i.index
                value = ''
                try:
                    value = self._references(i)
                    if (self.bslash_abort and value == '\\') or value == '/':
                        split_index.append((i.index - 2, 1))
                except StopIteration:
                    i.rewind(i.index - index)
            elif c == '/':
                split_index.append((i.index - 1, 0))
            elif c == '[':
                index = i.index
                try:
                    self._sequence(i)
                except StopIteration:
                    i.rewind(i.index - index)

        for split, offset in split_index:
            value = pattern[start + 1:split]
            self.store(value.encode('latin-1') if is_bytes else value, parts, True)  # type: ignore[arg-type]
            start = split + offset

        if start < len(pattern):
            value = pattern[start + 1:]
            if value:
                self.store(value.encode('latin-1') if is_bytes else value, parts, False)  # type: ignore[arg-type]

        if len(pattern) == 0:
            parts.append(
                _GlobPart(pattern.encode('latin-1') if is_bytes else pattern, False, False, False, False, False)
            )

        if (
            (self.extmatchbase and not parts[0].is_drive) or
            (self.matchbase and len(parts) == 1 and not parts[0].dir_only)
        ):
            if self.globstarlong and self.follow:
                gstar = b'***' if is_bytes else '***'  # type: Any
                is_globstarlong = True
            else:
                gstar = b'**' if is_bytes else '**'
                is_globstarlong = False
            parts.insert(0, _GlobPart(gstar, True, True, is_globstarlong, True, False))

        if self.no_abs and parts and parts[0].is_drive:
            raise ValueError('The pattern must be a relative path pattern')

        return parts


class Glob(Generic[AnyStr]):
    """Glob patterns."""

    def __init__(
        self,
        pattern: AnyStr | Sequence[AnyStr],
        flags: int = 0,
        root_dir: AnyStr | os.PathLike[AnyStr] | None = None,
        dir_fd: int | None = None,
        limit: int = _wcparse.PATTERN_LIMIT,
        exclude: AnyStr | Sequence[AnyStr] | None = None
    ) -> None:
        """Initialize the directory walker object."""

        pats = [pattern] if isinstance(pattern, (str, bytes)) else pattern
        epats = [exclude] if isinstance(exclude, (str, bytes)) else exclude

        if epats is not None:
            flags = _wcparse.no_negate_flags(flags)

        self.pattern = []  # type: list[list[_GlobPart]]
        self.npatterns = []  # type: list[Pattern[AnyStr]]
        self.seen = set()  # type: set[AnyStr]
        self.dir_fd = dir_fd if SUPPORT_DIR_FD else None  # type: int | None
        self.nounique = bool(flags & NOUNIQUE)  # type: bool
        self.mark = bool(flags & MARK)  # type: bool
        # Only scan for `.` and `..` if it is specifically requested.
        self.scandotdir = bool(flags & SCANDOTDIR)  # type: bool
        if self.mark:
            flags ^= MARK
        self.negateall = bool(flags & NEGATEALL)  # type: bool
        if self.negateall:
            flags ^= NEGATEALL
        self.nodir = bool(flags & NODIR)  # type: bool
        if self.nodir:
            flags ^= NODIR
        self.pathlib = bool(flags & _PATHLIB)  # type: bool
        if self.pathlib:
            flags ^= _PATHLIB
        self.flags = _flag_transform(flags | REALPATH)  # type: int
        self.negate_flags = self.flags | DOTMATCH | _wcparse._NO_GLOBSTAR_CAPTURE  # type: int
        if not self.scandotdir and not self.flags & NODOTDIR:
            self.flags |= NODOTDIR
        self.raw_chars = bool(self.flags & RAWCHARS)  # type: bool
        self.dot = bool(self.flags & DOTMATCH)  # type: bool
        self.unix = not bool(self.flags & FORCEWIN)  # type: bool
        self.negate = bool(self.flags & NEGATE)  # type: bool
        self.globstarlong = bool(self.flags & GLOBSTARLONG)  # type: bool
        self.globstar = self.globstarlong or bool(self.flags & GLOBSTAR)  # type: bool
        self.follow_links = bool(self.flags & FOLLOW) and not self.globstarlong  # type: bool
        self.braces = bool(self.flags & BRACE)  # type: bool
        self.matchbase = bool(self.flags & MATCHBASE)  # type: bool
        self.case_sensitive = _wcparse.get_case(self.flags)  # type: bool
        self.limit = limit  # type: int

        forcewin = self.flags & FORCEWIN
        if isinstance(pats[0], bytes):
            ptype = util.BYTES
            self.current = b'.'  # type: AnyStr
            self.specials = (b'.', b'..')  # type: tuple[AnyStr, ...]
            self.empty = b''  # type: AnyStr
            self.stars = b'**'  # type: AnyStr
            self.sep = b'\\' if forcewin else b'/'  # type: AnyStr
            self.seps = (b'/', self.sep) if forcewin else (self.sep,)  # type: tuple[AnyStr, ...]
            self.re_pathlib_norm = _RE_WIN_PATHLIB_DOT_NORM[ptype]  # type: Pattern[AnyStr]  # type: ignore[assignment]
            self.re_no_dir = _wcparse.RE_WIN_NO_DIR[ptype]  # type: Pattern[AnyStr]  # type: ignore[assignment]
        else:
            ptype = util.UNICODE
            self.current = '.'
            self.specials = ('.', '..')
            self.empty = ''
            self.stars = '**'
            self.sep = '\\' if forcewin else '/'
            self.seps = ('/', self.sep) if forcewin else (self.sep,)
            self.re_pathlib_norm = _RE_WIN_PATHLIB_DOT_NORM[ptype]  # type: ignore[assignment]
            self.re_no_dir = _wcparse.RE_WIN_NO_DIR[ptype]  # type: ignore[assignment]

        temp = os.fspath(root_dir) if root_dir is not None else self.current
        if not isinstance(temp, bytes if ptype else str):
            raise TypeError(
                f'Pattern and root_dir should be of the same type, not {type(pats[0])} and {type(temp)}'
            )

        self.root_dir = temp  # type: AnyStr
        self.current_limit = self.limit
        self._parse_patterns(pats)
        if epats is not None:
            self._parse_patterns(epats, force_negate=True)

    def _iter_patterns(self, patterns: Sequence[AnyStr], force_negate: bool = False) -> Iterator[tuple[bool, AnyStr]]:
        """Iterate expanded patterns."""

        seen = set()
        try:
            total = 0
            for p in patterns:
                p = util.norm_pattern(p, not self.unix, self.raw_chars)
                count = 0
                for expanded in _wcparse.expand(p, self.flags, self.current_limit):
                    count += 1
                    total += 1
                    if 0 < self.limit < total:
                        raise _wcparse.PatternLimitException(
                            f"Pattern limit exceeded the limit of {self.limit:d}"
                        )
                    # Filter out duplicate patterns. If `NOUNIQUE` is enabled,
                    # we only want to filter on negative patterns as they are
                    # only filters.
                    is_neg = force_negate or _wcparse.is_negative(expanded, self.flags)
                    if not self.nounique or is_neg:
                        if expanded in seen:
                            continue
                        seen.add(expanded)

                    yield is_neg, expanded[1:] if is_neg and not force_negate else expanded
                if self.limit:
                    self.current_limit -= count
                    if self.current_limit < 1:
                        self.current_limit = 1
        except bracex.ExpansionLimitException as e:
            raise _wcparse.PatternLimitException(
                f"Pattern limit exceeded the limit of {self.limit:d}"
            ) from e

    def _parse_patterns(self, patterns: Sequence[AnyStr], force_negate: bool = False) -> None:
        """Parse patterns."""

        for is_neg, p in self._iter_patterns(patterns, force_negate=force_negate):
            if is_neg:
                # Treat the inverse pattern as a normal pattern if it matches, we will exclude.
                # This is faster as compiled patterns usually compare the include patterns first,
                # and then the exclude, but glob will already know it wants to include the file.
                self.npatterns.append(_wcparse._compile(p, self.negate_flags))
            else:
                self.pattern.append(_GlobSplit(p, self.flags).split())

        if not self.pattern and self.npatterns:
            if self.negateall:
                default = self.stars
                self.pattern.append(_GlobSplit(default, self.flags | GLOBSTAR).split())

        if self.nodir and not force_negate:
            self.npatterns.append(self.re_no_dir)

        # A single positive pattern will not find multiples of the same file
        # disable unique mode so that we won't waste time or memory computing unique returns.
        if (
            not force_negate and
            len(self.pattern) <= 1 and
            not self.flags & NODOTDIR and
            not self.nounique and
            not (self.pathlib and self.scandotdir)
        ):
            self.nounique = True

    def _is_hidden(self, name: AnyStr) -> bool:
        """Check if is file hidden."""

        return not self.dot and name[0:1] == self.specials[0]

    def _is_this(self, name: AnyStr) -> bool:
        """Check if "this" directory `.`."""

        return name == self.specials[0] or name == self.sep

    def _is_parent(self, name: AnyStr) -> bool:
        """Check if `..`."""

        return name == self.specials[1]

    def _match_excluded(self, filename: AnyStr, is_dir: bool) -> bool:
        """Check if file should be excluded."""

        if is_dir and not filename.endswith(self.sep):
            filename += self.sep

        matched = False
        for pattern in self.npatterns:
            if pattern.fullmatch(filename):
                matched = True
                break

        return matched

    def _is_excluded(self, path: AnyStr, is_dir: bool) -> bool:
        """Check if file is excluded."""

        return bool(self.npatterns and self._match_excluded(path, is_dir))

    def _match_literal(self, a: AnyStr, b: AnyStr | None = None) -> bool:
        """Match two names."""

        return a.lower() == b if not self.case_sensitive else a == b

    def _get_matcher(self, target: AnyStr | Pattern[AnyStr] | None) -> Callable[..., Any] | None:
        """Get deep match."""

        if target is None:
            matcher = None  # type: Callable[..., Any] | None
        elif isinstance(target, (str, bytes)):
            # Plain text match
            if not self.case_sensitive:
                match = target.lower()
            else:
                match = target
            matcher = functools.partial(self._match_literal, b=match)
        else:
            # File match pattern
            matcher = target.match
        return matcher

    def _lexists(self, path: AnyStr) -> bool:
        """Check if file exists."""

        if not self.dir_fd:
            return os.path.lexists(self.prepend_base(path))
        try:
            os.lstat(self.prepend_base(path), dir_fd=self.dir_fd)
        except (OSError, ValueError):  # pragma: no cover
            return False
        else:
            return True

    def prepend_base(self, path: AnyStr) -> AnyStr:
        """Join path to base if pattern is not absolute."""

        if self.is_abs_pattern:
            return path
        else:
            return os.path.join(self.root_dir, path)

    def _iter(self, curdir: AnyStr | None, dir_only: bool, deep: bool) -> Iterator[tuple[AnyStr, bool, bool, bool]]:
        """Iterate the directory."""

        try:
            fd = None  # type: int | None
            if self.is_abs_pattern and curdir:
                scandir = curdir  # type: AnyStr | int
            elif self.dir_fd is not None:
                fd = scandir = os.open(
                    os.path.join(self.root_dir, curdir) if curdir else self.root_dir,
                    _wcmatch.DIR_FLAGS,
                    dir_fd=self.dir_fd
                )
            else:
                scandir = os.path.join(self.root_dir, curdir) if curdir else self.root_dir

            # Python will never return . or .., so fake it.
            for special in self.specials:
                yield special, True, True, False

            try:
                with os.scandir(scandir) as scan:
                    for f in scan:
                        try:
                            hidden = self._is_hidden(f.name)  # type: ignore[arg-type]
                            is_dir = f.is_dir()
                            if is_dir:
                                is_link = f.is_symlink()
                            else:
                                # We don't care if a file is a link
                                is_link = False
                            if (not dir_only or is_dir):
                                yield f.name, is_dir, hidden, is_link  # type: ignore[misc]
                        except OSError:  # pragma: no cover # noqa: PERF203
                            pass
            finally:
                if fd is not None:
                    os.close(fd)

        except OSError:  # pragma: no cover
            pass

    def _glob_dir(
        self,
        curdir: AnyStr,
        matcher: Callable[..., Any] | None,
        dir_only: bool = False,
        deep: bool = False,
        globstar_follow: bool = False
    ) -> Iterator[tuple[AnyStr, bool]]:
        """Recursive directory glob."""

        files = list(self._iter(curdir, dir_only, deep))
        for file, is_dir, hidden, is_link in files:
            if file in self.specials:
                if matcher is not None and matcher(file):
                    yield os.path.join(curdir, file), True
                continue

            path = os.path.join(curdir, file)
            if (matcher is None and not hidden) or (matcher and matcher(file)):
                yield path, is_dir

            follow = not is_link or self.follow_links or globstar_follow
            if deep and not hidden and is_dir and follow:
                yield from self._glob_dir(path, matcher, dir_only, deep, globstar_follow)

    def _glob(self, curdir: AnyStr, part: _GlobPart, rest: list[_GlobPart]) -> Iterator[tuple[AnyStr, bool]]:
        """
        Handle glob flow.

        There are really only a couple of cases:

        - File name.
        - File name pattern (magic).
        - Directory.
        - Directory name pattern (magic).
        - Extra slashes `////`.
        - `globstar` `**`.
        """

        is_magic = part.is_magic
        dir_only = part.dir_only
        target = part.pattern
        is_globstar = part.is_globstar
        is_globstarlong = part.is_globstarlong

        if is_magic and is_globstar:
            # Glob star directory `**`.

            # Acquire the pattern after the `globstars` if available.
            # If not, mark that the `globstar` is the end.
            this = rest.pop(0) if rest else None
            globstar_end = this is None
            if this:
                dir_only = this.dir_only
                target = this.pattern

            if globstar_end:
                target = None

            # We match `**/next` during a deep glob, so what ever comes back,
            # we will send back through `_glob` with pattern after `next` (`**/next/after`).
            # So grab `after` if available.
            this = rest.pop(0) if rest else None

            # Deep searching is the unique case where we
            # might feed in a `None` for the next pattern to match.
            # Deep glob will account for this.
            matcher = self._get_matcher(target)

            # If our pattern ends with `curdir/**`, but does not start with `**` it matches zero or more,
            # so it should return `curdir/`, signifying `curdir` + no match.
            # If a pattern follows `**/something`, we always get the appropriate
            # return already, so this isn't needed in that case.
            # There is one quirk though with Bash, if `curdir` had magic before `**`, Bash
            # omits the trailing `/`. We don't worry about that.
            if globstar_end and curdir:
                yield os.path.join(curdir, self.empty), True

            # Search
            for path, is_dir in self._glob_dir(curdir, matcher, dir_only, deep=True, globstar_follow=is_globstarlong):
                if this:
                    yield from self._glob(path, this, rest[:])
                else:
                    yield path, is_dir

        elif not dir_only:
            # Files: no need to recursively search at this point as we are done.
            matcher = self._get_matcher(target)
            yield from self._glob_dir(curdir, matcher)

        else:
            # Directory: search current directory against pattern
            # and feed the results back through with the next pattern.
            this = rest.pop(0) if rest else None
            matcher = self._get_matcher(target)
            for path, is_dir in self._glob_dir(curdir, matcher, True):
                if this:
                    yield from self._glob(path, this, rest[:])
                else:
                    yield path, is_dir

    def _get_starting_paths(self, curdir: AnyStr, dir_only: bool) -> list[tuple[AnyStr, bool]]:
        """
        Get the starting location.

        For case sensitive paths, we have to "glob" for
        it first as Python doesn't like for its users to
        think about case. By scanning for it, we can get
        the actual casing and then compare.
        """

        if not self.is_abs_pattern and not self._is_parent(curdir) and not self._is_this(curdir):
            results = []
            matcher = self._get_matcher(curdir)
            files = list(self._iter(None, dir_only, False))
            for file, is_dir, _hidden, _is_link in files:
                if file not in self.specials and (matcher is None or matcher(file)):
                    results.append((file, is_dir))
        else:
            results = [(curdir, True)]
        return results

    def is_unique(self, path: AnyStr) -> bool:
        """Test if path is unique."""

        if self.nounique:
            return True

        unique = False
        if (path.lower() if not self.case_sensitive else path) not in self.seen:
            self.seen.add(path)
            unique = True
        return unique

    def _pathlib_norm(self, path: AnyStr) -> AnyStr:
        """Normalize path as `pathlib` does."""

        path = self.re_pathlib_norm.sub(self.empty, path)
        return path[:-1] if len(path) > 1 and path[-1:] in self.seps else path

    def format_path(self, path: AnyStr, is_dir: bool, dir_only: bool) -> Iterator[AnyStr]:
        """Format path."""

        path = os.path.join(path, self.empty) if dir_only or (self.mark and is_dir) else path
        if self.is_unique(self._pathlib_norm(path) if self.pathlib else path):
            yield path

    def glob(self) -> Iterator[AnyStr]:
        """Starts off the glob iterator."""

        for pattern in self.pattern:
            curdir = self.current

            # If the pattern ends with `/` we return the files ending with `/`.
            dir_only = pattern[-1].dir_only if pattern else False
            self.is_abs_pattern = pattern[0].is_drive if pattern else False

            if pattern:
                if not pattern[0].is_magic:
                    # Path starts with normal plain text
                    # Lets verify the case of the starting directory (if possible)
                    this = pattern[0]
                    curdir = this[0]

                    # Abort if we cannot find the drive, or if current directory is empty
                    if not curdir or (self.is_abs_pattern and not self._lexists(self.prepend_base(curdir))):
                        continue

                    # Make sure case matches, but running case insensitive
                    # on a case sensitive file system may return more than
                    # one starting location.
                    results = self._get_starting_paths(curdir, dir_only)
                    if not results:
                        continue

                    if this.dir_only:
                        # Glob these directories if they exists
                        for start, is_dir in results:
                            rest = pattern[1:]
                            if rest:
                                this = rest.pop(0)
                                for match, is_dir in self._glob(start, this, rest):
                                    if not self._is_excluded(match, is_dir):
                                        yield from self.format_path(match, is_dir, dir_only)
                            elif not self._is_excluded(start, is_dir):
                                yield from self.format_path(start, is_dir, dir_only)
                    else:
                        # Return the file(s) and finish.
                        for match, is_dir in results:
                            if self._lexists(match) and not self._is_excluded(match, is_dir):
                                yield from self.format_path(match, is_dir, dir_only)
                else:
                    # Path starts with a magic pattern, let's get globbing
                    rest = pattern[:]
                    this = rest.pop(0)
                    for match, is_dir in self._glob(curdir if not curdir == self.current else self.empty, this, rest):
                        if not self._is_excluded(match, is_dir):
                            yield from self.format_path(match, is_dir, dir_only)


def iglob(
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    root_dir: AnyStr | os.PathLike[AnyStr] | None = None,
    dir_fd: int | None = None,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> Iterator[AnyStr]:
    """Glob."""

    if not isinstance(patterns, (str, bytes)) and not patterns:
        return

    yield from Glob(patterns, flags, root_dir, dir_fd, limit, exclude).glob()


def glob(
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    root_dir: AnyStr | os.PathLike[AnyStr] | None = None,
    dir_fd: int | None = None,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> list[AnyStr]:
    """Glob."""

    return list(iglob(patterns, flags=flags, root_dir=root_dir, dir_fd=dir_fd, limit=limit, exclude=exclude))


def translate(
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> tuple[list[AnyStr], list[AnyStr]]:
    """Translate glob pattern."""

    flags = _flag_transform(flags)
    return _wcparse.translate(patterns, flags, limit, exclude)


def globmatch(
    filename: AnyStr | os.PathLike[AnyStr],
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    root_dir: AnyStr | os.PathLike[AnyStr] | None = None,
    dir_fd: int | None = None,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> bool:
    """
    Check if filename matches pattern.

    By default case sensitivity is determined by the file system,
    but if `case_sensitive` is set, respect that instead.
    """

    # Shortcut out if we have no patterns
    if not patterns:
        return False

    rdir = os.fspath(root_dir) if root_dir is not None else root_dir
    flags = _flag_transform(flags)
    fname = os.fspath(filename)

    return bool(_wcparse.compile(patterns, flags, limit, exclude).match(fname, rdir, dir_fd))


def globfilter(
    filenames: Iterable[AnyStr | os.PathLike[AnyStr]],
    patterns: AnyStr | Sequence[AnyStr],
    *,
    flags: int = 0,
    root_dir: AnyStr | os.PathLike[AnyStr] | None = None,
    dir_fd: int | None = None,
    limit: int = _wcparse.PATTERN_LIMIT,
    exclude: AnyStr | Sequence[AnyStr] | None = None
) -> list[AnyStr | os.PathLike[AnyStr]]:
    """Filter names using pattern."""

    # Shortcut out if we have no patterns
    if not patterns:
        return []

    rdir = os.fspath(root_dir) if root_dir is not None else root_dir

    matches = []  # type: list[AnyStr | os.PathLike[AnyStr]]
    flags = _flag_transform(flags)
    obj = _wcparse.compile(patterns, flags, limit, exclude)

    for filename in filenames:
        temp = os.fspath(filename)
        if obj.match(temp, rdir, dir_fd):
            matches.append(filename)
    return matches


def escape(pattern: AnyStr, unix: bool | None = None) -> AnyStr:
    """Escape."""

    return _wcparse.escape(pattern, unix=unix)


def is_magic(pattern: AnyStr, *, flags: int = 0) -> bool:
    """Check if the pattern is likely to be magic."""

    flags = _flag_transform(flags)
    return _wcparse.is_magic(pattern, flags)
