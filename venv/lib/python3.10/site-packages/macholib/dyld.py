"""
dyld emulation
"""

import ctypes
import os
import platform
import sys
from itertools import chain

from macholib.dylib import dylib_info
from macholib.framework import framework_info

__all__ = ["dyld_find", "framework_find", "framework_info", "dylib_info"]

if sys.platform == "darwin" and [
    int(x) for x in platform.mac_ver()[0].split(".")[:2]
] >= [10, 16]:
    try:
        libc = ctypes.CDLL("libSystem.dylib")

    except OSError:
        _dyld_shared_cache_contains_path = None

    else:
        try:
            _dyld_shared_cache_contains_path = libc._dyld_shared_cache_contains_path
        except AttributeError:
            _dyld_shared_cache_contains_path = None

        else:
            _dyld_shared_cache_contains_path.restype = ctypes.c_bool
            _dyld_shared_cache_contains_path.argtypes = [ctypes.c_char_p]

            if sys.version_info[0] != 2:
                __dyld_shared_cache_contains_path = _dyld_shared_cache_contains_path

                def _dyld_shared_cache_contains_path(path):
                    return __dyld_shared_cache_contains_path(path.encode())

else:
    _dyld_shared_cache_contains_path = None

# These are the defaults as per man dyld(1)
#
_DEFAULT_FRAMEWORK_FALLBACK = [
    os.path.expanduser("~/Library/Frameworks"),
    "/Library/Frameworks",
    "/Network/Library/Frameworks",
    "/System/Library/Frameworks",
]

_DEFAULT_LIBRARY_FALLBACK = [
    os.path.expanduser("~/lib"),
    "/usr/local/lib",
    "/lib",
    "/usr/lib",
]

if sys.version_info[0] == 2:

    def _ensure_utf8(s):
        if isinstance(s, unicode):  # noqa: F821
            return s.encode("utf8")
        return s

else:

    def _ensure_utf8(s):
        if s is not None and not isinstance(s, str):
            raise ValueError(s)
        return s


def _dyld_env(env, var):
    if env is None:
        env = os.environ
    rval = env.get(var)
    if rval is None or rval == "":
        return []
    return rval.split(":")


def dyld_image_suffix(env=None):
    if env is None:
        env = os.environ
    return env.get("DYLD_IMAGE_SUFFIX")


def dyld_framework_path(env=None):
    return _dyld_env(env, "DYLD_FRAMEWORK_PATH")


def dyld_library_path(env=None):
    return _dyld_env(env, "DYLD_LIBRARY_PATH")


def dyld_fallback_framework_path(env=None):
    return _dyld_env(env, "DYLD_FALLBACK_FRAMEWORK_PATH")


def dyld_fallback_library_path(env=None):
    return _dyld_env(env, "DYLD_FALLBACK_LIBRARY_PATH")


def dyld_image_suffix_search(iterator, env=None):
    """For a potential path iterator, add DYLD_IMAGE_SUFFIX semantics"""
    suffix = dyld_image_suffix(env)
    if suffix is None:
        return iterator

    def _inject(iterator=iterator, suffix=suffix):
        for path in iterator:
            if path.endswith(".dylib"):
                yield path[: -len(".dylib")] + suffix + ".dylib"
            else:
                yield path + suffix
            yield path

    return _inject()


def dyld_override_search(name, env=None):
    # If DYLD_FRAMEWORK_PATH is set and this dylib_name is a
    # framework name, use the first file that exists in the framework
    # path if any.  If there is none go on to search the DYLD_LIBRARY_PATH
    # if any.

    framework = framework_info(name)

    if framework is not None:
        for path in dyld_framework_path(env):
            yield os.path.join(path, framework["name"])

    # If DYLD_LIBRARY_PATH is set then use the first file that exists
    # in the path.  If none use the original name.
    for path in dyld_library_path(env):
        yield os.path.join(path, os.path.basename(name))


def dyld_executable_path_search(name, executable_path=None):
    # If we haven't done any searching and found a library and the
    # dylib_name starts with "@executable_path/" then construct the
    # library name.
    if name.startswith("@executable_path/") and executable_path is not None:
        yield os.path.join(
            executable_path, name[len("@executable_path/") :]  # noqa: E203
        )


def dyld_loader_search(name, loader_path=None):
    # If we haven't done any searching and found a library and the
    # dylib_name starts with "@loader_path/" then construct the
    # library name.
    if name.startswith("@loader_path/") and loader_path is not None:
        yield os.path.join(loader_path, name[len("@loader_path/") :])  # noqa: E203


def dyld_default_search(name, env=None):
    yield name

    framework = framework_info(name)

    if framework is not None:
        fallback_framework_path = dyld_fallback_framework_path(env)

        if fallback_framework_path:
            for path in fallback_framework_path:
                yield os.path.join(path, framework["name"])

        else:
            for path in _DEFAULT_FRAMEWORK_FALLBACK:
                yield os.path.join(path, framework["name"])

    fallback_library_path = dyld_fallback_library_path(env)
    if fallback_library_path:
        for path in fallback_library_path:
            yield os.path.join(path, os.path.basename(name))

    else:
        for path in _DEFAULT_LIBRARY_FALLBACK:
            yield os.path.join(path, os.path.basename(name))


def dyld_find(name, executable_path=None, env=None, loader_path=None):
    """
    Find a library or framework using dyld semantics
    """
    name = _ensure_utf8(name)
    executable_path = _ensure_utf8(executable_path)
    for path in dyld_image_suffix_search(
        chain(
            dyld_override_search(name, env),
            dyld_executable_path_search(name, executable_path),
            dyld_loader_search(name, loader_path),
            dyld_default_search(name, env),
        ),
        env,
    ):
        if (
            _dyld_shared_cache_contains_path is not None
            and _dyld_shared_cache_contains_path(path)
        ):
            return path
        if os.path.isfile(path):
            return path
    raise ValueError("dylib %s could not be found" % (name,))


def framework_find(fn, executable_path=None, env=None):
    """
    Find a framework using dyld semantics in a very loose manner.

    Will take input such as:
        Python
        Python.framework
        Python.framework/Versions/Current
    """
    try:
        return dyld_find(fn, executable_path=executable_path, env=env)
    except ValueError:
        pass
    fmwk_index = fn.rfind(".framework")
    if fmwk_index == -1:
        fmwk_index = len(fn)
        fn += ".framework"
    fn = os.path.join(fn, os.path.basename(fn[:fmwk_index]))
    return dyld_find(fn, executable_path=executable_path, env=env)
