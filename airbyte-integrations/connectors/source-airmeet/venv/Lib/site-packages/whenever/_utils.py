"""Misc public utilities, e.g. to manage the timezone cache, or patch the time"""

from __future__ import annotations

import os.path  # NOTE: we don't use pathlib here to keep our imports light
import sysconfig
from contextlib import contextmanager
from functools import partial
from typing import Any, Iterable, Iterator, Union, no_type_check

from ._core import (
    Instant,
    OffsetDateTime,
    SystemDateTime,
    ZonedDateTime,
    _clear_tz_cache,
    _clear_tz_cache_by_keys,
    _patch_time_frozen,
    _patch_time_keep_ticking,
    _set_tzpath,
    _unpatch_time,
)

# Maintainer's notes:
# - Yes I dislike the name `utils` too, but it seems to fit OK in this case.
# - These functions are implemented in Python regardless of whether the rust
#   extension is active. This is fine because they are not performance-critical,
#   and build upon the core API.


__all__ = [
    "patch_current_time",
    "reset_tzpath",
    "clear_tzcache",
    "available_timezones",
]


class _TimePatch:
    _pin: Union[Instant, ZonedDateTime, OffsetDateTime, SystemDateTime]
    _keep_ticking: bool

    def __init__(
        self,
        pin: Union[Instant, ZonedDateTime, OffsetDateTime, SystemDateTime],
        keep_ticking: bool,
    ):
        self._pin = pin
        self._keep_ticking = keep_ticking

    # NOTE: permissively typechecked, but that's OK for a testing utility
    def shift(self, *args: Any, **kwargs: Any) -> None:
        if self._keep_ticking:
            self._pin = new = (
                self._pin + (Instant.now() - self._pin)  # type: ignore[operator]
            ).add(*args, **kwargs)
            _patch_time_keep_ticking(
                new if isinstance(new, Instant) else new.to_instant()
            )
        else:
            self._pin = new = self._pin.add(*args, **kwargs)
            _patch_time_frozen(
                new if isinstance(new, Instant) else new.to_instant()
            )


@contextmanager
def patch_current_time(
    dt: Union[Instant, ZonedDateTime, OffsetDateTime, SystemDateTime],
    /,
    *,
    keep_ticking: bool,
) -> Iterator[_TimePatch]:
    """Patch the current time to a fixed value (for testing purposes).
    Behaves as a context manager or decorator, with similar semantics to
    ``unittest.mock.patch``.

    Important
    ---------

    * This function should be used only for testing purposes. It is not
      thread-safe or part of the stable API.
    * This function only affects whenever's ``now`` functions. It does not
      affect the standard library's time functions or any other libraries.
      Use the ``time_machine`` package if you also want to patch other libraries.
    * It doesn't affect the system timezone.
      If you need to patch the system timezone, set the ``TZ`` environment
      variable in combination with ``time.tzset``. Be aware that this only
      works on Unix-like systems.

    Example
    -------

    >>> from whenever import Instant, patch_current_time
    >>> i = Instant.from_utc(1980, 3, 2, hour=2)
    >>> with patch_current_time(i, keep_ticking=False) as p:
    ...     assert Instant.now() == i
    ...     p.shift(hours=4)
    ...     assert i.now() == i.add(hours=4)
    ...
    >>> assert Instant.now() != i
    ...
    >>> @patch_current_time(i, keep_ticking=True)
    ... def test_thing(p):
    ...     assert (Instant.now() - i) < seconds(1)
    ...     p.shift(hours=8)
    ...     sleep(0.000001)
    ...     assert hours(8) < (Instant.now() - i) < hours(8.1)
    """
    instant = dt if isinstance(dt, Instant) else dt.to_instant()
    if keep_ticking:
        _patch_time_keep_ticking(instant)
    else:
        _patch_time_frozen(instant)

    try:
        yield _TimePatch(dt, keep_ticking)
    finally:
        _unpatch_time()


TZPATH: tuple[str, ...] = ()


def reset_tzpath(
    target: Iterable[str | os.PathLike[str]] | None = None, /
) -> None:
    """Reset or set the paths in which ``whenever`` will search for timezone data.

    It does not affect the :mod:`zoneinfo` module or other libraries.

    Note
    ----
    Due to caching, you may find that looking up a timezone after setting the tzpath
    doesn't load the timezone data from the new path. You may need to call
    :func:`clear_tzcache` if you want to force loading *all* timezones from the new path.
    Note that clearing the cache may have unexpected side effects, however.

    Behaves similarly to :func:`zoneinfo.reset_tzpath`
    """
    global TZPATH

    if target is not None:
        # This is such a common mistake, that we raise a descriptive error
        if isinstance(target, (str, bytes)):
            raise TypeError("tzpath must be an iterable of paths")

        if not all(map(os.path.isabs, target)):
            raise ValueError("tzpaths must be absolute paths")
        # mypy doesn't seem to follow, but it appears correct
        TZPATH = tuple(map(os.fspath, target))  # type: ignore[arg-type]
    else:
        TZPATH = _tzpath_from_env()
    _set_tzpath(TZPATH)


def _tzpath_from_env() -> tuple[str, ...]:
    try:
        env_var = os.environ["PYTHONTZPATH"]
    except KeyError:
        env_var = sysconfig.get_config_var("TZPATH")

    # FUTURE: include in test coverage
    if not env_var:
        return ()  # pragma: no cover

    raw_tzpath = env_var.split(os.pathsep)
    # according to spec, we're allowed to silently ignore invalid paths
    new_tzpath = tuple(filter(os.path.isabs, raw_tzpath))
    return new_tzpath


def clear_tzcache(*, only_keys: Iterable[str] | None = None) -> None:
    """Clear the timezone cache. If ``only_keys`` is provided, only the cache for those
    keys will be cleared.

    Caution
    -------
    Calling this function may change the behavior of existing ``ZonedDateTime``
    instances in surprising ways. Most significantly, the
    ``exact_eq()`` method will return ``False`` between instances created before and after clearing the cache.

    **Use this function only if you know that you need to.**

    Behaves similarly to :meth:`zoneinfo.ZoneInfo.clear_cache`.
    """
    if only_keys is None:
        _clear_tz_cache()
    else:
        _clear_tz_cache_by_keys(tuple(only_keys))


def available_timezones() -> set[str]:
    """Gather the set of all available timezones.

    Each call to this function will recalculate the available timezone names
    depending on the currently configured ``TZPATH``, and the
    presence of the ``tzdata`` package.

    Warning
    -------
    This function may open a large number of files, since the first few bytes
    of timezone files must be read to determine if they are valid.

    Note
    ----

    This function behaves similarly to :func:`zoneinfo.available_timezones`,
    which means it ignores the "special" zones (e.g. posixrules, right/posix, etc.)

    It should give the same result as :func:`zoneinfo.available_timezones`,
    unless ``whenever`` was configured to use a different tzpath
    using :func:`reset_tzpath`.

    """
    zones: set[str] = set()
    # Get the zones from the tzdata package, if available
    try:
        # NOTE: we don't use importlib.resources here,
        # to keep our imports lighter
        tzdata = __import__("tzdata").__path__[0]
        with open(os.path.join(tzdata, "zones")) as f:
            zones.update(map(str.strip, f))
    # coverage note: we *do* test tzdata and non-tzdata installs in CI
    except (ImportError, FileNotFoundError):  # pragma: no cover
        pass

    # Get the zones from the tzpath directories
    for base in TZPATH:
        zones.update(_find_all_tznames(base))

    zones.discard("posixrules")  # a special file that shouldn't be included
    return zones


# Recursively find all tzfiles in the tzpath directories.
# Recursion is safe here since the file tree is trusted, and nesting doesn't
# even approach the recursion limit.
# NOTE: we don't use pathlib here, since we want to keep our imports light
def _find_all_tznames(base: str) -> Iterator[str]:
    if not os.path.isdir(base):
        return
    for name in os.listdir(base):
        entry = os.path.join(base, name)
        if os.path.isdir(entry):
            # FUTURE: expand test coverage for this
            if name in ("right", "posix"):  # pragma: no cover
                # These directories contain special files that shouldn't be included
                continue
            else:
                for path in _find_nested_tzfiles(entry):
                    yield os.path.relpath(path, base).replace("\\", "/")
        elif _is_tzifile(entry):
            yield name


def _find_nested_tzfiles(path: str) -> Iterator[str]:
    assert os.path.isdir(path)
    for name in os.listdir(path):
        entry = os.path.join(path, name)
        if os.path.isdir(entry):
            yield from _find_nested_tzfiles(entry)
        elif _is_tzifile(entry):
            yield entry


def _is_tzifile(p: str) -> bool:
    """Check if the file is a tzifile."""
    try:
        with open(p, "rb") as f:
            return f.read(4) == b"TZif"
    except OSError:  # pragma: no cover
        return False


@no_type_check
def _pydantic_parse(cls: type, v: object) -> object:
    # exact type comparison is OK: whenever types don't allow subclassing
    if type(v) is cls:
        return v
    # whenever also doesn't allow string subclasses
    elif type(v) is str:
        return cls.parse_common_iso(v)
    else:
        raise ValueError(f"Cannot parse {cls.__name__} from type {type(v)}")


@no_type_check
def pydantic_schema(cls):
    from pydantic_core import core_schema

    return core_schema.json_or_python_schema(
        # NOTE: We can't use no_info_plain_validator_function here, because
        # this breaks JSON schema generation...but only when used with the
        # "serialization" mode for some reason...
        json_schema=core_schema.no_info_after_validator_function(
            cls.parse_common_iso,
            core_schema.str_schema(strict=True),
            serialization=core_schema.to_string_ser_schema(),
        ),
        python_schema=core_schema.no_info_plain_validator_function(
            partial(_pydantic_parse, cls),
            # NOTE: not setting serializer here somehow breaks the JSON schema
            # generation when defaults are present...yeah...
            serialization=core_schema.to_string_ser_schema(),
        ),
    )
