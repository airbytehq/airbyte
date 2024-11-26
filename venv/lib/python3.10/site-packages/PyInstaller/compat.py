# ----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# ----------------------------------------------------------------------------
"""
Various classes and functions to provide some backwards-compatibility with previous versions of Python onward.
"""
from __future__ import annotations

import errno

import importlib.machinery
import importlib.util
import os
import platform
import site
import subprocess
import sys
import shutil
import types

from PyInstaller._shared_with_waf import _pyi_machine
from PyInstaller.exceptions import ExecCommandFailed

# setup.py sets this environment variable to avoid errors due to unmet run-time dependencies. The PyInstaller.compat
# module is imported by setup.py to build wheels, and some dependencies that are otherwise required at run-time
# (importlib-metadata on python < 3.10, pywin32-ctypes on Windows) might not be present while building wheels,
# nor are they required during that phase.
_setup_py_mode = os.environ.get('_PYINSTALLER_SETUP_PY', '0') != '0'

# PyInstaller requires importlib.metadata from python >= 3.10 stdlib, or equivalent importlib-metadata >= 4.6.
if _setup_py_mode:
    importlib_metadata = None
else:
    if sys.version_info >= (3, 10):
        import importlib.metadata as importlib_metadata
    else:
        try:
            import importlib_metadata
        except ImportError as e:
            from PyInstaller.exceptions import ImportlibMetadataError
            raise ImportlibMetadataError() from e

        import packaging.version  # For importlib_metadata version check

        # Validate the version
        if packaging.version.parse(importlib_metadata.version("importlib-metadata")) < packaging.version.parse("4.6"):
            from PyInstaller.exceptions import ImportlibMetadataError
            raise ImportlibMetadataError()

# Strict collect mode, which raises error when trying to collect duplicate files into PKG/CArchive or COLLECT.
strict_collect_mode = os.environ.get("PYINSTALLER_STRICT_COLLECT_MODE", "0") != "0"

# Copied from https://docs.python.org/3/library/platform.html#cross-platform.
is_64bits: bool = sys.maxsize > 2**32

# Distinguish specific code for various Python versions. Variables 'is_pyXY' mean that Python X.Y and up is supported.
# Keep even unsupported versions here to keep 3rd-party hooks working.
is_py35 = sys.version_info >= (3, 5)
is_py36 = sys.version_info >= (3, 6)
is_py37 = sys.version_info >= (3, 7)
is_py38 = sys.version_info >= (3, 8)
is_py39 = sys.version_info >= (3, 9)
is_py310 = sys.version_info >= (3, 10)
is_py311 = sys.version_info >= (3, 11)
is_py312 = sys.version_info >= (3, 12)

is_win = sys.platform.startswith('win')
is_win_10 = is_win and (platform.win32_ver()[0] == '10')
is_win_wine = False  # Running under Wine; determined later on.
is_cygwin = sys.platform == 'cygwin'
is_darwin = sys.platform == 'darwin'  # Mac OS X

# Unix platforms
is_linux = sys.platform.startswith('linux')
is_solar = sys.platform.startswith('sun')  # Solaris
is_aix = sys.platform.startswith('aix')
is_freebsd = sys.platform.startswith('freebsd')
is_openbsd = sys.platform.startswith('openbsd')
is_hpux = sys.platform.startswith('hp-ux')

# Some code parts are similar to several unix platforms (e.g. Linux, Solaris, AIX).
# Mac OS is not considered as unix since there are many platform-specific details for Mac in PyInstaller.
is_unix = is_linux or is_solar or is_aix or is_freebsd or is_hpux or is_openbsd

# Linux distributions such as Alpine or OpenWRT use musl as their libc implementation and resultantly need specially
# compiled bootloaders. On musl systems, ldd with no arguments prints 'musl' and its version.
is_musl = is_linux and "musl" in subprocess.run(["ldd"], capture_output=True, encoding="utf-8").stderr

# macOS version
_macos_ver = tuple(int(x) for x in platform.mac_ver()[0].split('.')) if is_darwin else None

# macOS 11 (Big Sur): if python is not compiled with Big Sur support, it ends up in compatibility mode by default, which
# is indicated by platform.mac_ver() returning '10.16'. The lack of proper Big Sur support breaks find_library()
# function from ctypes.util module, as starting with Big Sur, shared libraries are not visible on disk anymore. Support
# for the new library search mechanism was added in python 3.9 when compiled with Big Sur support. In such cases,
# platform.mac_ver() reports version as '11.x'. The behavior can be further modified via SYSTEM_VERSION_COMPAT
# environment variable; which allows explicitly enabling or disabling the compatibility mode. However, note that
# disabling the compatibility mode and using python that does not properly support Big Sur still leaves find_library()
# broken (which is a scenario that we ignore at the moment).
# The same logic applies to macOS 12 (Monterey).
is_macos_11_compat = bool(_macos_ver) and _macos_ver[0:2] == (10, 16)  # Big Sur or newer in compat mode
is_macos_11_native = bool(_macos_ver) and _macos_ver[0:2] >= (11, 0)  # Big Sur or newer in native mode
is_macos_11 = is_macos_11_compat or is_macos_11_native  # Big Sur or newer

# On different platforms is different file for dynamic python library.
_pyver = sys.version_info[:2]
if is_win or is_cygwin:
    PYDYLIB_NAMES = {
        'python%d%d.dll' % _pyver,
        'libpython%d%d.dll' % _pyver,
        'libpython%d.%d.dll' % _pyver,
    }  # For MSYS2 environment
elif is_darwin:
    # libpython%d.%dm.dylib for Conda virtual environment installations
    PYDYLIB_NAMES = {
        'Python',
        '.Python',
        'Python%d' % _pyver[0],
        'libpython%d.%d.dylib' % _pyver,
    }
elif is_aix:
    # Shared libs on AIX may be archives with shared object members, hence the ".a" suffix. However, starting with
    # python 2.7.11 libpython?.?.so and Python3 libpython?.?m.so files are produced.
    PYDYLIB_NAMES = {
        'libpython%d.%d.a' % _pyver,
        'libpython%d.%d.so' % _pyver,
    }
elif is_freebsd:
    PYDYLIB_NAMES = {
        'libpython%d.%d.so.1' % _pyver,
        'libpython%d.%d.so.1.0' % _pyver,
    }
elif is_openbsd:
    PYDYLIB_NAMES = {'libpython%d.%d.so.0.0' % _pyver}
elif is_hpux:
    PYDYLIB_NAMES = {'libpython%d.%d.so' % _pyver}
elif is_unix:
    # Other *nix platforms.
    # Python 2 .so library on Linux is: libpython2.7.so.1.0
    # Python 3 .so library on Linux is: libpython3.3.so.1.0
    PYDYLIB_NAMES = {'libpython%d.%d.so.1.0' % _pyver, 'libpython%d.%d.so' % _pyver}
else:
    raise SystemExit('Your platform is not yet supported. Please define constant PYDYLIB_NAMES for your platform.')

# In a virtual environment created by virtualenv (github.com/pypa/virtualenv) there exists sys.real_prefix with the path
# to the base Python installation from which the virtual environment was created. This is true regardless of the version
# of Python used to execute the virtualenv command.
#
# In a virtual environment created by the venv module available in the Python standard lib, there exists sys.base_prefix
# with the path to the base implementation. This does not exist in a virtual environment created by virtualenv.
#
# The following code creates compat.is_venv and is.virtualenv that are True when running a virtual environment, and also
# compat.base_prefix with the path to the base Python installation.

base_prefix: str = os.path.abspath(getattr(sys, 'real_prefix', getattr(sys, 'base_prefix', sys.prefix)))
# Ensure `base_prefix` is not containing any relative parts.
is_venv = is_virtualenv = base_prefix != os.path.abspath(sys.prefix)

# Conda environments sometimes have different paths or apply patches to packages that can affect how a hook or package
# should access resources. Method for determining conda taken from https://stackoverflow.com/questions/47610844#47610844
is_conda = os.path.isdir(os.path.join(base_prefix, 'conda-meta'))

# Similar to ``is_conda`` but is ``False`` using another ``venv``-like manager on top. In this case, no packages
# encountered will be conda packages meaning that the default non-conda behaviour is generally desired from PyInstaller.
is_pure_conda = os.path.isdir(os.path.join(sys.prefix, 'conda-meta'))

# Full path to python interpreter.
python_executable = getattr(sys, '_base_executable', sys.executable)

# Is this Python from Microsoft App Store (Windows only)? Python from Microsoft App Store has executable pointing at
# empty shims.
is_ms_app_store = is_win and os.path.getsize(python_executable) == 0

if is_ms_app_store:
    # Locate the actual executable inside base_prefix.
    python_executable = os.path.join(base_prefix, os.path.basename(python_executable))
    if not os.path.exists(python_executable):
        raise SystemExit(
            'PyInstaller cannot locate real python executable belonging to Python from Microsoft App Store!'
        )

# Bytecode magic value
BYTECODE_MAGIC = importlib.util.MAGIC_NUMBER

# List of suffixes for Python C extension modules.
EXTENSION_SUFFIXES = importlib.machinery.EXTENSION_SUFFIXES
ALL_SUFFIXES = importlib.machinery.all_suffixes()

# On Windows we require pywin32-ctypes.
# -> all pyinstaller modules should use win32api from PyInstaller.compat to
#    ensure that it can work on MSYS2 (which requires pywin32-ctypes)
if is_win:
    if _setup_py_mode:
        pywintypes = None
        win32api = None
    else:
        try:
            from win32ctypes.pywin32 import pywintypes  # noqa: F401, E402
            from win32ctypes.pywin32 import win32api  # noqa: F401, E402
        except ImportError as e:
            raise SystemExit(
                'PyInstaller cannot check for assembly dependencies.\n'
                'Please install pywin32-ctypes.\n\n'
                'pip install pywin32-ctypes\n'
            ) from e
        except Exception as e:
            if sys.flags.optimize == 2:
                raise SystemExit(
                    "pycparser, a Windows only indirect dependency of PyInstaller, is incompatible with "
                    "Python's \"discard docstrings\" (-OO) flag mode. For more information see:\n"
                    "    https://github.com/pyinstaller/pyinstaller/issues/6345"
                ) from e
            raise

# macOS's platform.architecture() can be buggy, so we do this manually here. Based off the python documentation:
# https://docs.python.org/3/library/platform.html#platform.architecture
if is_darwin:
    architecture = '64bit' if sys.maxsize > 2**32 else '32bit'
else:
    architecture = platform.architecture()[0]

# Cygwin needs special handling, because platform.system() contains identifiers such as MSYS_NT-10.0-19042 and
# CYGWIN_NT-10.0-19042 that do not fit PyInstaller's OS naming scheme. Explicitly set `system` to 'Cygwin'.
system = 'Cygwin' if is_cygwin else platform.system()

# Machine suffix for bootloader.
machine = _pyi_machine(platform.machine(), platform.system())


# Wine detection and support
def is_wine_dll(filename: str | os.PathLike):
    """
    Check if the given PE file is a Wine DLL (PE-converted built-in, or fake/placeholder one).

    Returns True if the given file is a Wine DLL, False if not (or if file cannot be analyzed or does not exist).
    """
    _WINE_SIGNATURES = (
        b'Wine builtin DLL',  # PE-converted Wine DLL
        b'Wine placeholder DLL',  # Fake/placeholder Wine DLL
    )
    _MAX_LEN = max([len(sig) for sig in _WINE_SIGNATURES])

    # Wine places their DLL signature in the padding area between the IMAGE_DOS_HEADER and IMAGE_NT_HEADERS. So we need
    # to compare the bytes that come right after IMAGE_DOS_HEADER, i.e., after initial 64 bytes. We can read the file
    # directly and avoid using the pefile library to avoid performance penalty associated with full header parsing.
    try:
        with open(filename, 'rb') as fp:
            fp.seek(64)
            signature = fp.read(_MAX_LEN)
        return signature.startswith(_WINE_SIGNATURES)
    except Exception:
        pass
    return False


if is_win:
    try:
        import ctypes.util  # noqa: E402
        is_win_wine = is_wine_dll(ctypes.util.find_library('kernel32'))
    except Exception:
        pass

# Set and get environment variables does not handle unicode strings correctly on Windows.

# Acting on os.environ instead of using getenv()/setenv()/unsetenv(), as suggested in
# <http://docs.python.org/library/os.html#os.environ>: "Calling putenv() directly does not change os.environ, so it is
# better to modify os.environ." (Same for unsetenv.)


def getenv(name: str, default: str | None = None):
    """
    Returns unicode string containing value of environment variable 'name'.
    """
    return os.environ.get(name, default)


def setenv(name: str, value: str):
    """
    Accepts unicode string and set it as environment variable 'name' containing value 'value'.
    """
    os.environ[name] = value


def unsetenv(name: str):
    """
    Delete the environment variable 'name'.
    """
    # Some platforms (e.g., AIX) do not support `os.unsetenv()` and thus `del os.environ[name]` has no effect on the
    # real environment. For this case, we set the value to the empty string.
    os.environ[name] = ""
    del os.environ[name]


# Exec commands in subprocesses.


def exec_command(
    *cmdargs: str, encoding: str | None = None, raise_enoent: bool | None = None, **kwargs: int | bool | list | None
):
    """
    Run the command specified by the passed positional arguments, optionally configured by the passed keyword arguments.

    .. DANGER::
       **Ignore this function's return value** -- unless this command's standard output contains _only_ pathnames, in
       which case this function returns the correct filesystem-encoded string expected by PyInstaller. In all other
       cases, this function's return value is _not_ safely usable. Consider calling the general-purpose
       `exec_command_stdout()` function instead.

       For backward compatibility, this function's return value non-portably depends on the current Python version and
       passed keyword arguments:

       * Under Python 2.7, this value is an **encoded `str` string** rather than a decoded `unicode` string. This value
         _cannot_ be safely used for any purpose (e.g., string manipulation or parsing), except to be passed directly to
         another non-Python command.
       * Under Python 3.x, this value is a **decoded `str` string**. However, even this value is _not_ necessarily
         safely usable:
         * If the `encoding` parameter is passed, this value is guaranteed to be safely usable.
         * Else, this value _cannot_ be safely used for any purpose (e.g., string manipulation or parsing), except to be
           passed directly to another non-Python command. Why? Because this value has been decoded with the encoding
           specified by `sys.getfilesystemencoding()`, the encoding used by `os.fsencode()` and `os.fsdecode()` to
           convert from platform-agnostic to platform-specific pathnames. This is _not_ necessarily the encoding with
           which this command's standard output was encoded. Cue edge-case decoding exceptions.

    Parameters
    ----------
    cmdargs :
        Variadic list whose:
        1. Mandatory first element is the absolute path, relative path, or basename in the current `${PATH}` of the
           command to run.
        2. Optional remaining elements are arguments to pass to this command.
    encoding : str, optional
        Optional keyword argument specifying the encoding with which to decode this command's standard output under
        Python 3. As this function's return value should be ignored, this argument should _never_ be passed.
    raise_enoent : boolean, optional
        Optional keyword argument to simply raise the exception if the executing the command fails since to the command
        is not found. This is useful to checking id a command exists.

    All remaining keyword arguments are passed as is to the `subprocess.Popen()` constructor.

    Returns
    ----------
    str
        Ignore this value. See discussion above.
    """

    proc = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, **kwargs)
    try:
        out = proc.communicate(timeout=60)[0]
    except OSError as e:
        if raise_enoent and e.errno == errno.ENOENT:
            raise
        print('--' * 20, file=sys.stderr)
        print("Error running '%s':" % " ".join(cmdargs), file=sys.stderr)
        print(e, file=sys.stderr)
        print('--' * 20, file=sys.stderr)
        raise ExecCommandFailed("Error: Executing command failed!") from e
    except subprocess.TimeoutExpired:
        proc.kill()
        raise

    # stdout/stderr are returned as a byte array NOT as string, so we need to convert that to proper encoding.
    try:
        if encoding:
            out = out.decode(encoding)
        else:
            # If no encoding is given, assume we are reading filenames from stdout only because it is the common case.
            out = os.fsdecode(out)
    except UnicodeDecodeError as e:
        # The sub-process used a different encoding; provide more information to ease debugging.
        print('--' * 20, file=sys.stderr)
        print(str(e), file=sys.stderr)
        print('These are the bytes around the offending byte:', file=sys.stderr)
        print('--' * 20, file=sys.stderr)
        raise
    return out


def exec_command_rc(*cmdargs: str, **kwargs: float | bool | list | None):
    """
    Return the exit code of the command specified by the passed positional arguments, optionally configured by the
    passed keyword arguments.

    Parameters
    ----------
    cmdargs : list
        Variadic list whose:
        1. Mandatory first element is the absolute path, relative path, or basename in the current `${PATH}` of the
           command to run.
        2. Optional remaining elements are arguments to pass to this command.

    All keyword arguments are passed as is to the `subprocess.call()` function.

    Returns
    ----------
    int
        This command's exit code as an unsigned byte in the range `[0, 255]`, where 0 signifies success and all other
        values signal a failure.
    """

    # 'encoding' keyword is not supported for 'subprocess.call'; remove it from kwargs.
    if 'encoding' in kwargs:
        kwargs.pop('encoding')
    return subprocess.call(cmdargs, **kwargs)


def exec_command_all(*cmdargs: str, encoding: str | None = None, **kwargs: int | bool | list | None):
    """
    Run the command specified by the passed positional arguments, optionally configured by the passed keyword arguments.

    .. DANGER::
       **Ignore this function's return value.** If this command's standard output consists solely of pathnames, consider
       calling `exec_command()`; otherwise, consider calling `exec_command_stdout()`.

    Parameters
    ----------
    cmdargs : str
        Variadic list whose:
        1. Mandatory first element is the absolute path, relative path, or basename in the current `${PATH}` of the
           command to run.
        2. Optional remaining elements are arguments to pass to this command.
    encoding : str, optional
        Optional keyword argument specifying the encoding with which to decode this command's standard output. As this
        function's return value should be ignored, this argument should _never_ be passed.

    All remaining keyword arguments are passed as is to the `subprocess.Popen()` constructor.

    Returns
    ----------
    (int, str, str)
        Ignore this 3-element tuple `(exit_code, stdout, stderr)`. See the `exec_command()` function for discussion.
    """
    proc = subprocess.Popen(
        cmdargs,
        bufsize=-1,  # Default OS buffer size.
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs
    )
    # Waits for subprocess to complete.
    try:
        out, err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise
    # stdout/stderr are returned as a byte array NOT as string. Thus we need to convert that to proper encoding.
    try:
        if encoding:
            out = out.decode(encoding)
            err = err.decode(encoding)
        else:
            # If no encoding is given, assume we're reading filenames from stdout only because it's the common case.
            out = os.fsdecode(out)
            err = os.fsdecode(err)
    except UnicodeDecodeError as e:
        # The sub-process used a different encoding, provide more information to ease debugging.
        print('--' * 20, file=sys.stderr)
        print(str(e), file=sys.stderr)
        print('These are the bytes around the offending byte:', file=sys.stderr)
        print('--' * 20, file=sys.stderr)
        raise

    return proc.returncode, out, err


def __wrap_python(args, kwargs):
    cmdargs = [sys.executable]

    # Mac OS X supports universal binaries (binary for multiple architectures. We need to ensure that subprocess
    # binaries are running for the same architecture as python executable. It is necessary to run binaries with 'arch'
    # command.
    if is_darwin:
        if architecture == '64bit':
            if platform.machine() == 'arm64':
                py_prefix = ['arch', '-arm64']  # Apple M1
            else:
                py_prefix = ['arch', '-x86_64']  # Intel
        elif architecture == '32bit':
            py_prefix = ['arch', '-i386']
        else:
            py_prefix = []
        # Since Mac OS 10.11, the environment variable DYLD_LIBRARY_PATH is no more inherited by child processes, so we
        # proactively propagate the current value using the `-e` option of the `arch` command.
        if 'DYLD_LIBRARY_PATH' in os.environ:
            path = os.environ['DYLD_LIBRARY_PATH']
            py_prefix += ['-e', 'DYLD_LIBRARY_PATH=%s' % path]
        cmdargs = py_prefix + cmdargs

    if not __debug__:
        cmdargs.append('-O')

    cmdargs.extend(args)

    env = kwargs.get('env')
    if env is None:
        env = dict(**os.environ)

    # Ensure python 3 subprocess writes 'str' as utf-8
    env['PYTHONIOENCODING'] = 'UTF-8'
    # ... and ensure we read output as utf-8
    kwargs['encoding'] = 'UTF-8'

    return cmdargs, kwargs


def exec_python(*args: str, **kwargs: str | None):
    """
    Wrap running python script in a subprocess.

    Return stdout of the invoked command.
    """
    cmdargs, kwargs = __wrap_python(args, kwargs)
    return exec_command(*cmdargs, **kwargs)


def exec_python_rc(*args: str, **kwargs: str | None):
    """
    Wrap running python script in a subprocess.

    Return exit code of the invoked command.
    """
    cmdargs, kwargs = __wrap_python(args, kwargs)
    return exec_command_rc(*cmdargs, **kwargs)


# Path handling.


def expand_path(path: str | os.PathLike):
    """
    Replace initial tilde '~' in path with user's home directory, and also expand environment variables
    (i.e., ${VARNAME} on Unix, %VARNAME% on Windows).
    """
    return os.path.expandvars(os.path.expanduser(path))


# Site-packages functions - use native function if available.
def getsitepackages(prefixes: list | None = None):
    """
    Returns a list containing all global site-packages directories.

    For each directory present in ``prefixes`` (or the global ``PREFIXES``), this function finds its `site-packages`
    subdirectory depending on the system environment, and returns a list of full paths.
    """
    # This implementation was copied from the ``site`` module, python 3.7.3.
    sitepackages = []
    seen = set()

    if prefixes is None:
        prefixes = [sys.prefix, sys.exec_prefix]

    for prefix in prefixes:
        if not prefix or prefix in seen:
            continue
        seen.add(prefix)

        if os.sep == '/':
            sitepackages.append(os.path.join(prefix, "lib", "python%d.%d" % sys.version_info[:2], "site-packages"))
        else:
            sitepackages.append(prefix)
            sitepackages.append(os.path.join(prefix, "lib", "site-packages"))
    return sitepackages


# Backported for virtualenv. Module 'site' in virtualenv might not have this attribute.
getsitepackages = getattr(site, 'getsitepackages', getsitepackages)


# Wrapper to load a module from a Python source file. This function loads import hooks when processing them.
def importlib_load_source(name: str, pathname: str):
    # Import module from a file.
    mod_loader = importlib.machinery.SourceFileLoader(name, pathname)
    mod = types.ModuleType(mod_loader.name)
    mod.__file__ = mod_loader.get_filename()  # Some hooks require __file__ attribute in their namespace
    mod_loader.exec_module(mod)
    return mod


# Patterns of module names that should be bundled into the base_library.zip to be available during bootstrap.
# These modules include direct or indirect dependencies of encodings.* modules. The encodings modules must be
# recursively included to set the I/O encoding during python startup. Similarly, this list should include
# modules used by PyInstaller's bootstrap scripts and modules (loader/pyi*.py)

PY3_BASE_MODULES = {
    '_collections_abc',
    '_weakrefset',
    'abc',
    'codecs',
    'collections',
    'copyreg',
    'encodings',
    'enum',
    'functools',
    'genericpath',  # dependency of os.path
    'io',
    'heapq',
    'keyword',
    'linecache',
    'locale',
    'ntpath',  # dependency of os.path
    'operator',
    'os',
    'posixpath',  # dependency of os.path
    're',
    'reprlib',
    'sre_compile',
    'sre_constants',
    'sre_parse',
    'stat',  # dependency of os.path
    'traceback',  # for startup errors
    'types',
    'weakref',
    'warnings',
}

if not is_py310:
    PY3_BASE_MODULES.add('_bootlocale')

# Object types of Pure Python modules in modulegraph dependency graph.
# Pure Python modules have code object (attribute co_code).
PURE_PYTHON_MODULE_TYPES = {
    'SourceModule',
    'CompiledModule',
    'Package',
    'NamespacePackage',
    # Deprecated.
    # TODO Could these module types be removed?
    'FlatPackage',
    'ArchiveModule',
}
# Object types of special Python modules (built-in, run-time, namespace package) in modulegraph dependency graph that do
# not have code object.
SPECIAL_MODULE_TYPES = {
    'AliasNode',
    'BuiltinModule',
    'RuntimeModule',
    'RuntimePackage',

    # PyInstaller handles scripts differently and not as standard Python modules.
    'Script',
}
# Object types of Binary Python modules (extensions, etc) in modulegraph dependency graph.
BINARY_MODULE_TYPES = {
    'Extension',
    'ExtensionPackage',
}
# Object types of valid Python modules in modulegraph dependency graph.
VALID_MODULE_TYPES = PURE_PYTHON_MODULE_TYPES | SPECIAL_MODULE_TYPES | BINARY_MODULE_TYPES
# Object types of bad/missing/invalid Python modules in modulegraph dependency graph.
# TODO: should be 'Invalid' module types also in the 'MISSING' set?
BAD_MODULE_TYPES = {
    'BadModule',
    'ExcludedModule',
    'InvalidSourceModule',
    'InvalidCompiledModule',
    'MissingModule',

    # Runtime modules and packages are technically valid rather than bad, but exist only in-memory rather than on-disk
    # (typically due to pre_safe_import_module() hooks), and hence cannot be physically frozen. For simplicity, these
    # nodes are categorized as bad rather than valid.
    'RuntimeModule',
    'RuntimePackage',
}
ALL_MODULE_TYPES = VALID_MODULE_TYPES | BAD_MODULE_TYPES
# TODO: review this mapping to TOC, remove useless entries.
# Dictionary to map ModuleGraph node types to TOC typecodes.
MODULE_TYPES_TO_TOC_DICT = {
    # Pure modules.
    'AliasNode': 'PYMODULE',
    'Script': 'PYSOURCE',
    'SourceModule': 'PYMODULE',
    'CompiledModule': 'PYMODULE',
    'Package': 'PYMODULE',
    'FlatPackage': 'PYMODULE',
    'ArchiveModule': 'PYMODULE',
    # Binary modules.
    'Extension': 'EXTENSION',
    'ExtensionPackage': 'EXTENSION',
    # Special valid modules.
    'BuiltinModule': 'BUILTIN',
    'NamespacePackage': 'PYMODULE',
    # Bad modules.
    'BadModule': 'bad',
    'ExcludedModule': 'excluded',
    'InvalidSourceModule': 'invalid',
    'InvalidCompiledModule': 'invalid',
    'MissingModule': 'missing',
    'RuntimeModule': 'runtime',
    'RuntimePackage': 'runtime',
    # Other.
    'does not occur': 'BINARY',
}


def check_requirements():
    """
    Verify that all requirements to run PyInstaller are met.

    Fail hard if any requirement is not met.
    """
    # Fail hard if Python does not have minimum required version
    if sys.version_info < (3, 8):
        raise EnvironmentError('PyInstaller requires Python 3.8 or newer.')

    # There are some old packages which used to be backports of libraries which are now part of the standard library.
    # These backports are now unmaintained and contain only an older subset of features leading to obscure errors like
    # "enum has not attribute IntFlag" if installed.
    from importlib.metadata import distribution, PackageNotFoundError

    for name in ["enum34", "typing", "pathlib"]:
        try:
            dist = distribution(name)
        except PackageNotFoundError:
            continue
        remove = "conda remove" if is_conda else f'"{sys.executable}" -m pip uninstall {name}'
        raise SystemExit(
            f"The '{name}' package is an obsolete backport of a standard library package and is incompatible with "
            f"PyInstaller. Please remove this package (located in {dist.locate_file('')}) using\n    {remove}\n"
            "then try again."
        )

    # Bail out if binutils is not installed.
    if is_linux and shutil.which("objdump") is None:
        raise SystemExit(
            "On Linux, objdump is required. It is typically provided by the 'binutils' package "
            "installable via your Linux distribution's package manager."
        )
