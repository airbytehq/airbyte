"""Handle path matching."""
from __future__ import annotations
import re
import os
import stat
import copyreg
from . import util
from typing import Pattern, AnyStr, Generic, Any

# `O_DIRECTORY` may not always be defined
DIR_FLAGS = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0)
# Right half can return an empty set if not supported
SUPPORT_DIR_FD = {os.open, os.stat} <= os.supports_dir_fd and os.scandir in os.supports_fd

RE_WIN_MOUNT = (
    re.compile(r'\\|/|[a-z]:(?:\\|/|$)', re.I),
    re.compile(br'\\|/|[a-z]:(?:\\|/|$)', re.I)
)
RE_MOUNT = (
    re.compile(r'/'),
    re.compile(br'/')
)
RE_WIN_SPLIT = (
    re.compile(r'\\|/'),
    re.compile(br'\\|/')
)
RE_SPLIT = (
    re.compile(r'/'),
    re.compile(br'/')
)
RE_WIN_STRIP = (
    r'\\/',
    br'\\/'
)
RE_STRIP = (
    r'/',
    br'/'
)


class _Match(Generic[AnyStr]):
    """Match the given pattern."""

    def __init__(
        self,
        filename: AnyStr,
        include: tuple[Pattern[AnyStr], ...],
        exclude: tuple[Pattern[AnyStr], ...] | None,
        real: bool,
        path: bool,
        follow: bool
    ) -> None:
        """Initialize."""

        self.filename = filename  # type: AnyStr
        self.include = include  # type: tuple[Pattern[AnyStr], ...]
        self.exclude = exclude  # type: tuple[Pattern[AnyStr], ...] | None
        self.real = real
        self.path = path
        self.follow = follow
        self.ptype = util.BYTES if isinstance(self.filename, bytes) else util.UNICODE

    def _fs_match(
        self,
        pattern: Pattern[AnyStr],
        filename: AnyStr,
        is_win: bool,
        follow: bool,
        symlinks: dict[tuple[int | None, AnyStr], bool],
        root: AnyStr,
        dir_fd: int | None
    ) -> bool:
        """
        Match path against the pattern.

        Since `globstar` doesn't match symlinks (unless `FOLLOW` is enabled), we must look for symlinks.
        If we identify a symlink in a `globstar` match, we know this result should not actually match.

        We only check for the symlink if we know we are looking at a directory.
        And we only call `lstat` if we can't find it in the cache.

        We know we need to check the directory if:

        1. If the match has not reached the end of the path and directory is in `globstar` match.
        2. Or the match is at the end of the path and the directory is not the last part of `globstar` match.

        """

        matched = False
        split = (RE_WIN_SPLIT if is_win else RE_SPLIT)[self.ptype]  # type: Any
        strip = (RE_WIN_STRIP if is_win else RE_STRIP)[self.ptype]  # type: Any

        end = len(filename) - 1
        base = None
        m = pattern.fullmatch(filename)
        if m:
            matched = True
            # Lets look at the captured `globstar` groups and see if that part of the path
            # contains symlinks.
            if not follow:
                try:
                    for i, star in enumerate(m.groups(), 1):
                        if star:
                            at_end = m.end(i) == end
                            parts = split.split(star.strip(strip))
                            if base is None:
                                base = os.path.join(root, filename[:m.start(i)])
                            last_part = len(parts)
                            for j, part in enumerate(parts, 1):
                                base = os.path.join(base, part)
                                key = (dir_fd, base)
                                if not at_end or (at_end and j != last_part):
                                    is_link = symlinks.get(key, None)
                                    if is_link is None:
                                        if dir_fd is None:
                                            is_link = os.path.islink(base)
                                            symlinks[key] = is_link
                                        else:
                                            try:
                                                st = os.lstat(base, dir_fd=dir_fd)
                                            except (OSError, ValueError):  # pragma: no cover
                                                is_link = False
                                            else:
                                                is_link = stat.S_ISLNK(st.st_mode)
                                            symlinks[key] = is_link
                                    matched = not is_link
                                    if not matched:
                                        break
                        if not matched:
                            break
                except OSError:  # pragma: no cover
                    matched = False
        return matched

    def _match_real(
        self,
        symlinks: dict[tuple[int | None, AnyStr], bool],
        root: AnyStr,
        dir_fd: int | None
    ) -> bool:
        """Match real filename includes and excludes."""

        is_win = util.platform() == "windows"

        if isinstance(self.filename, bytes):
            sep = b'/'
            is_dir = (RE_WIN_SPLIT if is_win else RE_SPLIT)[1].match(self.filename[-1:]) is not None
        else:
            sep = '/'
            is_dir = (RE_WIN_SPLIT if is_win else RE_SPLIT)[0].match(self.filename[-1:]) is not None

        try:
            if dir_fd is None:
                is_file_dir = os.path.isdir(os.path.join(root, self.filename))
            else:
                try:
                    st = os.stat(os.path.join(root, self.filename), dir_fd=dir_fd)
                except (OSError, ValueError):  # pragma: no cover
                    is_file_dir = False
                else:
                    is_file_dir = stat.S_ISDIR(st.st_mode)
        except OSError:  # pragma: no cover
            return False

        if not is_dir and is_file_dir:
            is_dir = True
            filename = self.filename + sep
        else:
            filename = self.filename

        matched = False
        for pattern in self.include:
            if self._fs_match(pattern, filename, is_win, self.follow, symlinks, root, dir_fd):
                matched = True
                break

        if matched:
            if self.exclude:
                for pattern in self.exclude:
                    if self._fs_match(pattern, filename, is_win, True, symlinks, root, dir_fd):
                        matched = False
                        break

        return matched

    def match(self, root_dir: AnyStr | None = None, dir_fd: int | None = None) -> bool:
        """Match."""

        if self.real:
            if isinstance(self.filename, bytes):
                root = root_dir if root_dir is not None else b'.'  # type: AnyStr
            else:
                root = root_dir if root_dir is not None else '.'

            if dir_fd is not None and not SUPPORT_DIR_FD:
                dir_fd = None

            if not isinstance(self.filename, type(root)):
                raise TypeError(
                    "The filename and root directory should be of the same type, not {} and {}".format(
                        type(self.filename), type(root_dir)
                    )
                )

            if self.include and not isinstance(self.include[0].pattern, type(self.filename)):
                raise TypeError(
                    "The filename and pattern should be of the same type, not {} and {}".format(
                        type(self.filename), type(self.include[0].pattern)
                    )
                )

            re_mount = (RE_WIN_MOUNT if util.platform() == "windows" else RE_MOUNT)[self.ptype]  # type: Pattern[AnyStr]  # type: ignore[assignment]
            is_abs = re_mount.match(self.filename) is not None

            if is_abs:
                exists = os.path.lexists(self.filename)
            elif dir_fd is None:
                exists = os.path.lexists(os.path.join(root, self.filename))
            else:
                try:
                    os.lstat(os.path.join(root, self.filename), dir_fd=dir_fd)
                except (OSError, ValueError):  # pragma: no cover
                    exists = False
                else:
                    exists = True

            if exists:
                symlinks = {}  # type: dict[tuple[int | None, AnyStr], bool]
                return self._match_real(symlinks, root, dir_fd)
            else:
                return False

        matched = False
        for pattern in self.include:
            if pattern.fullmatch(self.filename):
                matched = True
                break

        if matched:
            matched = True
            if self.exclude:
                for pattern in self.exclude:
                    if pattern.fullmatch(self.filename):
                        matched = False
                        break
        return matched


class WcRegexp(util.Immutable, Generic[AnyStr]):
    """File name match object."""

    _include: tuple[Pattern[AnyStr], ...]
    _exclude: tuple[Pattern[AnyStr], ...] | None
    _real: bool
    _path: bool
    _follow: bool
    _hash: int

    __slots__ = ("_include", "_exclude", "_real", "_path", "_follow", "_hash")

    def __init__(
        self,
        include: tuple[Pattern[AnyStr], ...],
        exclude: tuple[Pattern[AnyStr], ...] | None = None,
        real: bool = False,
        path: bool = False,
        follow: bool = False
    ):
        """Initialization."""

        super().__init__(
            _include=include,
            _exclude=exclude,
            _real=real,
            _path=path,
            _follow=follow,
            _hash=hash(
                (
                    type(self),
                    type(include), include,
                    type(exclude), exclude,
                    type(real), real,
                    type(path), path,
                    type(follow), follow
                )
            )
        )

    def __hash__(self) -> int:
        """Hash."""

        return self._hash

    def __len__(self) -> int:
        """Length."""

        return len(self._include) + (len(self._exclude) if self._exclude is not None else 0)

    def __eq__(self, other: Any) -> bool:
        """Equal."""

        return (
            isinstance(other, WcRegexp) and
            self._include == other._include and
            self._exclude == other._exclude and
            self._real == other._real and
            self._path == other._path and
            self._follow == other._follow
        )

    def __ne__(self, other: Any) -> bool:
        """Equal."""

        return (
            not isinstance(other, WcRegexp) or
            self._include != other._include or
            self._exclude != other._exclude or
            self._real != other._real or
            self._path != other._path or
            self._follow != other._follow
        )

    def match(self, filename: AnyStr, root_dir: AnyStr | None = None, dir_fd: int | None = None) -> bool:
        """Match filename."""

        return _Match(
            filename,
            self._include,
            self._exclude,
            self._real,
            self._path,
            self._follow
        ).match(
            root_dir=root_dir,
            dir_fd=dir_fd
        )


def _pickle(p):  # type: ignore[no-untyped-def]
    return WcRegexp, (p._include, p._exclude, p._real, p._path, p._follow)


copyreg.pickle(WcRegexp, _pickle)
