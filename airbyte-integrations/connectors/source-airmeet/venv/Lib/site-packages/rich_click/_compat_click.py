from __future__ import annotations

import warnings

import click


try:
    with warnings.catch_warnings():
        warnings.simplefilter(category=DeprecationWarning, action="ignore")
        click_version = click.__version__
except Exception:
    # Click 9+ deprecated __version__, so all these checks must necessarily be False if __version__ doesn't exist.
    CLICK_IS_BEFORE_VERSION_821 = False
    CLICK_IS_BEFORE_VERSION_82 = False
    CLICK_IS_BEFORE_VERSION_9X = False
    CLICK_IS_VERSION_80 = False
else:
    _major = int(click_version.split(".")[0])  # type: ignore[attr-defined,unused-ignore]
    _minor = int(click_version.split(".")[1])  # type: ignore[attr-defined,unused-ignore]
    _patch = int(click_version.split(".")[2])  # type: ignore[attr-defined,unused-ignore]

    CLICK_IS_BEFORE_VERSION_821 = (_major, _minor, _patch) < (8, 2, 1)
    CLICK_IS_BEFORE_VERSION_82 = (_major, _minor) < (8, 2)
    CLICK_IS_BEFORE_VERSION_9X = _major < 9
    CLICK_IS_VERSION_80 = (_major, _minor) == (8, 0)
