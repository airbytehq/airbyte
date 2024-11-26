#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from __future__ import annotations

import copy
import os
import subprocess
import textwrap
import fnmatch
from pathlib import Path
from collections import deque
from typing import Callable

import packaging.requirements

from PyInstaller import HOMEPATH, compat
from PyInstaller import log as logging
from PyInstaller.depend.imphookapi import PostGraphAPI
from PyInstaller.exceptions import ExecCommandFailed
from PyInstaller import isolated
from PyInstaller.compat import importlib_metadata

logger = logging.getLogger(__name__)

# These extensions represent Python executables and should therefore be ignored when collecting data files.
# NOTE: .dylib files are not Python executable and should not be in this list.
PY_IGNORE_EXTENSIONS = set(compat.ALL_SUFFIXES)

# Some hooks need to save some values. This is the dict that can be used for that.
#
# When running tests this variable should be reset before every test.
#
# For example the 'wx' module needs variable 'wxpubsub'. This tells PyInstaller which protocol of the wx module
# should be bundled.
hook_variables = {}


def __exec_python_cmd(cmd, env=None, capture_stdout=True):
    """
    Executes an externally spawned Python interpreter. If capture_stdout is set to True, returns anything that was
    emitted in the standard output as a single string. Otherwise, returns the exit code.
    """
    # 'PyInstaller.config' cannot be imported as other top-level modules.
    from PyInstaller.config import CONF
    if env is None:
        env = {}
    # Update environment. Defaults to 'os.environ'
    pp_env = copy.deepcopy(os.environ)
    pp_env.update(env)
    # Prepend PYTHONPATH with pathex.
    # Some functions use some PyInstaller code in subprocess, so add PyInstaller HOMEPATH to sys.path as well.
    pp = os.pathsep.join(CONF['pathex'] + [HOMEPATH])

    # PYTHONPATH might be already defined in the 'env' argument or in the original 'os.environ'. Prepend it.
    if 'PYTHONPATH' in pp_env:
        pp = os.pathsep.join([pp_env.get('PYTHONPATH'), pp])
    pp_env['PYTHONPATH'] = pp

    if capture_stdout:
        txt = compat.exec_python(*cmd, env=pp_env)
        return txt.strip()
    else:
        return compat.exec_python_rc(*cmd, env=pp_env)


def __exec_statement(statement, capture_stdout=True):
    statement = textwrap.dedent(statement)
    cmd = ['-c', statement]
    return __exec_python_cmd(cmd, capture_stdout=capture_stdout)


def exec_statement(statement: str):
    """
    Execute a single Python statement in an externally-spawned interpreter, and return the resulting standard output
    as a string.

    Examples::

        tk_version = exec_statement("from _tkinter import TK_VERSION; print(TK_VERSION)")

        mpl_data_dir = exec_statement("import matplotlib; print(matplotlib.get_data_path())")
        datas = [ (mpl_data_dir, "") ]

    Notes:
        As of v5.0, usage of this function is discouraged in favour of the
        new :mod:`PyInstaller.isolated` module.

    """
    return __exec_statement(statement, capture_stdout=True)


def exec_statement_rc(statement: str):
    """
    Executes a Python statement in an externally spawned interpreter, and returns the exit code.
    """
    return __exec_statement(statement, capture_stdout=False)


def eval_statement(statement: str):
    """
    Execute a single Python statement in an externally-spawned interpreter, and :func:`eval` its output (if any).

    Example::

      databases = eval_statement('''
         import sqlalchemy.databases
         print(sqlalchemy.databases.__all__)
         ''')
      for db in databases:
         hiddenimports.append("sqlalchemy.databases." + db)

    Notes:
        As of v5.0, usage of this function is discouraged in favour of the
        new :mod:`PyInstaller.isolated` module.

    """
    txt = exec_statement(statement).strip()
    if not txt:
        # Return an empty string, which is "not true" but is iterable.
        return ''
    return eval(txt)


@isolated.decorate
def get_pyextension_imports(module_name: str):
    """
    Return list of modules required by binary (C/C++) Python extension.

    Python extension files ends with .so (Unix) or .pyd (Windows). It is almost impossible to analyze binary extension
    and its dependencies.

    Module cannot be imported directly.

    Let's at least try import it in a subprocess and observe the difference in module list from sys.modules.

    This function could be used for 'hiddenimports' in PyInstaller hooks files.
    """
    import sys
    import importlib

    original = set(sys.modules.keys())

    # When importing this module - sys.modules gets updated.
    importlib.import_module(module_name)

    # Find and return which new modules have been loaded.
    return list(set(sys.modules.keys()) - original - {module_name})


def get_homebrew_path(formula: str = ''):
    """
    Return the homebrew path to the requested formula, or the global prefix when called with no argument.

    Returns the path as a string or None if not found.
    """
    import subprocess
    brewcmd = ['brew', '--prefix']
    path = None
    if formula:
        brewcmd.append(formula)
        dbgstr = 'homebrew formula "%s"' % formula
    else:
        dbgstr = 'homebrew prefix'
    try:
        path = subprocess.check_output(brewcmd).strip()
        logger.debug('Found %s at "%s"' % (dbgstr, path))
    except OSError:
        logger.debug('Detected homebrew not installed')
    except subprocess.CalledProcessError:
        logger.debug('homebrew formula "%s" not installed' % formula)
    if path:
        return path.decode('utf8')  # Mac OS filenames are UTF-8
    else:
        return None


def remove_prefix(string: str, prefix: str):
    """
    This function removes the given prefix from a string, if the string does indeed begin with the prefix; otherwise,
    it returns the original string.
    """
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string


def remove_suffix(string: str, suffix: str):
    """
    This function removes the given suffix from a string, if the string does indeed end with the suffix; otherwise,
    it returns the original string.
    """
    # Special case: if suffix is empty, string[:0] returns ''. So, test for a non-empty suffix.
    if suffix and string.endswith(suffix):
        return string[:-len(suffix)]
    else:
        return string


# TODO: Do we really need a helper for this? This is pretty trivially obvious.
def remove_file_extension(filename: str):
    """
    This function returns filename without its extension.

    For Python C modules it removes even whole '.cpython-34m.so' etc.
    """
    for suff in compat.EXTENSION_SUFFIXES:
        if filename.endswith(suff):
            return filename[0:filename.rfind(suff)]
    # Fallback to ordinary 'splitext'.
    return os.path.splitext(filename)[0]


@isolated.decorate
def can_import_module(module_name: str):
    """
    Check if the specified module can be imported.

    Intended as a silent module availability check, as it does not print ModuleNotFoundError traceback to stderr when
    the module is unavailable.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module.

    Returns
    ----------
    bool
        Boolean indicating whether the module can be imported or not.
    """
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


# TODO: Replace most calls to exec_statement() with calls to this function.
def get_module_attribute(module_name: str, attr_name: str):
    """
    Get the string value of the passed attribute from the passed module if this attribute is defined by this module
    _or_ raise `AttributeError` otherwise.

    Since modules cannot be directly imported during analysis, this function spawns a subprocess importing this module
    and returning the string value of this attribute in this module.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of this module.
    attr_name : str
        Name of the attribute in this module to be retrieved.

    Returns
    ----------
    str
        String value of this attribute.

    Raises
    ----------
    AttributeError
        If this attribute is undefined.
    """
    @isolated.decorate
    def _get_module_attribute(module_name, attr_name):
        import importlib
        module = importlib.import_module(module_name)
        return getattr(module, attr_name)

    # Return AttributeError on any kind of errors, to preserve old behavior.
    try:
        return _get_module_attribute(module_name, attr_name)
    except Exception as e:
        raise AttributeError(f"Failed to retrieve attribute {attr_name} from module {module_name}") from e


def get_module_file_attribute(package: str):
    """
    Get the absolute path to the specified module or package.

    Modules and packages *must not* be directly imported in the main process during the analysis. Therefore, to
    avoid leaking the imports, this function uses an isolated subprocess when it needs to import the module and
    obtain its ``__file__`` attribute.

    Parameters
    ----------
    package : str
        Fully-qualified name of module or package.

    Returns
    ----------
    str
        Absolute path of this module.
    """
    # First, try to use 'importlib.util.find_spec' and obtain loader from the spec (and filename from the loader).
    # It is the fastest way, but does not work on certain modules in pywin32 that replace all module attributes with
    # those of the .dll. In addition, we need to avoid it for submodules/subpackages, because it ends up importing
    # their parent package, which would cause an import leak during the analysis.
    filename: str | None = None
    if '.' not in package:
        try:
            import importlib.util
            loader = importlib.util.find_spec(package).loader
            filename = loader.get_filename(package)
            # Apparently in the past, ``None`` could be returned for built-in ``datetime`` module. Just in case this
            # is still possible, return only if filename is valid.
            if filename:
                return filename
        except (ImportError, AttributeError, TypeError, ValueError):
            pass

    # Second attempt: try to obtain module/package's __file__ attribute in an isolated subprocess.
    @isolated.decorate
    def _get_module_file_attribute(package):
        # First, try to use 'importlib.util.find_spec' and obtain loader from the spec (and filename from the loader).
        # This should return the filename even if the module or package cannot be imported (e.g., a C-extension module
        # with missing dependencies).
        try:
            import importlib.util
            loader = importlib.util.find_spec(package).loader
            filename = loader.get_filename(package)
            # Safe-guard against ``None`` being returned (see comment in the non-isolated codepath).
            if filename:
                return filename
        except (ImportError, AttributeError, TypeError, ValueError):
            pass

        # Fall back to import attempt
        import importlib
        p = importlib.import_module(package)
        return p.__file__

    # The old behavior was to return ImportError (and that is what the test are also expecting...).
    try:
        filename = _get_module_file_attribute(package)
    except Exception as e:
        raise ImportError(f"Failed to obtain the __file__ attribute of package/module {package}!") from e

    return filename


def get_pywin32_module_file_attribute(module_name):
    """
    Get the absolute path of the PyWin32 DLL specific to the PyWin32 module with the passed name (`pythoncom`
    or `pywintypes`).

    On import, each PyWin32 module:

    * Imports a DLL specific to that module.
    * Overwrites the values of all module attributes with values specific to that DLL. This includes that module's
      `__file__` attribute, which then provides the absolute path of that DLL.

    This function imports the module in isolated subprocess and retrieves its `__file__` attribute.
    """

    # NOTE: we cannot use `get_module_file_attribute` as it does not account for the  __file__ rewriting magic
    # done by the module. Use `get_module_attribute` instead.
    return get_module_attribute(module_name, '__file__')


def check_requirement(requirement: str):
    """
    Check if a :pep:`0508` requirement is satisfied. Usually used to check if a package distribution is installed,
    or if it is installed and satisfies the specified version requirement.

    Parameters
    ----------
    requirement : str
        Requirement string in :pep:`0508` format.

    Returns
    ----------
    bool
        Boolean indicating whether the requirement is satisfied or not.

    Examples
    --------

    ::

        # Assume Pillow 10.0.0 is installed.
        >>> from PyInstaller.utils.hooks import check_requirement
        >>> check_requirement('Pillow')
        True
        >>> check_requirement('Pillow < 9.0')
        False
        >>> check_requirement('Pillow >= 9.0, < 11.0')
        True
    """
    parsed_requirement = packaging.requirements.Requirement(requirement)

    # Fetch the actual version of the specified dist
    try:
        version = importlib_metadata.version(parsed_requirement.name)
    except importlib_metadata.PackageNotFoundError:
        return False  # Not available at all

    # If specifier is not given, the only requirement is that dist is available
    if not parsed_requirement.specifier:
        return True

    # Parse specifier, and compare version. Enable pre-release matching,
    # because we need "package >= 2.0.0" to match "2.5.0b1".
    return parsed_requirement.specifier.contains(version, prereleases=True)


# Keep the `is_module_satisfies` as an alias for backwards compatibility with existing hooks. The old fallback
# to module version check does not work any more, though.
def is_module_satisfies(
    requirements: str,
    version: None = None,
    version_attr: None = None,
):
    """
    A compatibility wrapper for :func:`check_requirement`, intended for backwards compatibility with existing hooks.

    In contrast to original implementation from PyInstaller < 6, this implementation only checks the specified
    :pep:`0508` requirement string; i.e., it tries to retrieve the distribution metadata, and compare its version
    against optional version specifier(s). It does not attempt to fall back to checking the module's version attribute,
    nor does it support ``version`` and ``version_attr`` arguments.

    Parameters
    ----------
    requirements : str
        Requirements string passed to the :func:`check_requirement`.
    version : None
        Deprecated and unsupported. Must be ``None``.
    version_attr : None
        Deprecated and unsupported. Must be ``None``.

    Returns
    ----------
    bool
        Boolean indicating whether the requirement is satisfied or not.

    Raises
    ----------
    ValueError
        If either ``version`` or ``version_attr`` are specified and are not None.
    """
    if version is not None:
        raise ValueError("Calling is_module_satisfies with version argument is not supported anymore.")
    if version_attr is not None:
        raise ValueError("Calling is_module_satisfies with version argument_attr is not supported anymore.")
    return check_requirement(requirements)


def is_package(module_name: str):
    """
    Check if a Python module is really a module or is a package containing other modules, without importing anything
    in the main process.

    :param module_name: Module name to check.
    :return: True if module is a package else otherwise.
    """
    def _is_package(module_name: str):
        """
        Determines whether the given name represents a package or not. If the name represents a top-level module or
        a package, it is not imported. If the name represents a sub-module or a sub-package, its parent is imported.
        In such cases, this function should be called from an isolated suprocess.
        """
        try:
            import importlib.util
            spec = importlib.util.find_spec(module_name)
            return bool(spec.submodule_search_locations)
        except Exception:
            return False

    # For top-level packages/modules, we can perform check in the main process; otherwise, we need to isolate the
    # call to prevent import leaks in the main process.
    if '.' not in module_name:
        return _is_package(module_name)
    else:
        return isolated.call(_is_package, module_name)


def get_all_package_paths(package: str):
    """
    Given a package name, return all paths associated with the package. Typically, packages have a single location
    path, but PEP 420 namespace packages may be split across multiple locations. Returns an empty list if the specified
    package is not found or is not a package.
    """
    def _get_package_paths(package: str):
        """
        Retrieve package path(s), as advertised by submodule_search_paths attribute of the spec obtained via
        importlib.util.find_spec(package). If the name represents a top-level package, the package is not imported.
        If the name represents a sub-module or a sub-package, its parent is imported. In such cases, this function
        should be called from an isolated suprocess. Returns an empty list if specified package is not found or is not
        a package.
        """
        try:
            import importlib.util
            spec = importlib.util.find_spec(package)
            if not spec or not spec.submodule_search_locations:
                return []
            return [str(path) for path in spec.submodule_search_locations]
        except Exception:
            return []

    # For top-level packages/modules, we can perform check in the main process; otherwise, we need to isolate the
    # call to prevent import leaks in the main process.
    if '.' not in package:
        pkg_paths = _get_package_paths(package)
    else:
        pkg_paths = isolated.call(_get_package_paths, package)

    return pkg_paths


def package_base_path(package_path: str, package: str):
    """
    Given a package location path and package name, return the package base path, i.e., the directory in which the
    top-level package is located. For example, given the path ``/abs/path/to/python/libs/pkg/subpkg`` and
    package name ``pkg.subpkg``, the function returns ``/abs/path/to/python/libs``.
    """
    return remove_suffix(package_path, package.replace('.', os.sep))  # Base directory


def get_package_paths(package: str):
    """
    Given a package, return the path to packages stored on this machine and also returns the path to this particular
    package. For example, if pkg.subpkg lives in /abs/path/to/python/libs, then this function returns
    ``(/abs/path/to/python/libs, /abs/path/to/python/libs/pkg/subpkg)``.

    NOTE: due to backwards compatibility, this function returns only one package path along with its base directory.
    In case of PEP 420 namespace package with multiple location, only first location is returned. To obtain all
    package paths, use the ``get_all_package_paths`` function and obtain corresponding base directories using the
    ``package_base_path`` helper.
    """
    pkg_paths = get_all_package_paths(package)
    if not pkg_paths:
        raise ValueError(f"Package '{package}' does not exist or is not a package!")

    if len(pkg_paths) > 1:
        logger.warning(
            "get_package_paths - package %s has multiple paths (%r); returning only first one!", package, pkg_paths
        )

    pkg_dir = pkg_paths[0]
    pkg_base = package_base_path(pkg_dir, package)

    return pkg_base, pkg_dir


def collect_submodules(
    package: str,
    filter: Callable[[str], bool] = lambda name: True,
    on_error: str = "warn once",
):
    """
    List all submodules of a given package.

    Arguments:
        package:
            An ``import``-able package.
        filter:
            Filter the submodules found: A callable that takes a submodule name and returns True if it should be
            included.
        on_error:
            The action to take when a submodule fails to import. May be any of:

            - raise: Errors are reraised and terminate the build.
            - warn: Errors are downgraded to warnings.
            - warn once: The first error issues a warning but all
              subsequent errors are ignored to minimise *stderr pollution*. This
              is the default.
            - ignore: Skip all errors. Don't warn about anything.
    Returns:
        All submodules to be assigned to ``hiddenimports`` in a hook.

    This function is intended to be used by hook scripts, not by main PyInstaller code.

    Examples::

        # Collect all submodules of Sphinx don't contain the word ``test``.
        hiddenimports = collect_submodules(
            "Sphinx", ``filter=lambda name: 'test' not in name)

    .. versionchanged:: 4.5
        Add the **on_error** parameter.

    """
    # Accept only strings as packages.
    if not isinstance(package, str):
        raise TypeError('package must be a str')
    if on_error not in ("ignore", "warn once", "warn", "raise"):
        raise ValueError(
            f"Invalid on-error action '{on_error}': Must be one of ('ignore', 'warn once', 'warn', 'raise')"
        )

    logger.debug('Collecting submodules for %s', package)

    # Skip a module which is not a package.
    if not is_package(package):
        logger.debug('collect_submodules - %s is not a package.', package)
        # If module is importable, return its name in the list, in order to keep behavior consistent with the
        # one we have for packages (i.e., we include the package in the list of returned names)
        if can_import_module(package):
            return [package]
        return []

    # Determine the filesystem path(s) to the specified package.
    package_submodules = []

    todo = deque()
    todo.append(package)

    with isolated.Python() as isolated_python:
        while todo:
            # Scan the given (sub)package
            name = todo.pop()
            modules, subpackages, on_error = isolated_python.call(_collect_submodules, name, on_error)

            # Add modules to the list of all submodules
            package_submodules += [module for module in modules if filter(module)]

            # Add sub-packages to deque for subsequent recursion
            for subpackage_name in subpackages:
                if filter(subpackage_name):
                    todo.append(subpackage_name)

    package_submodules = sorted(package_submodules)

    logger.debug("collect_submodules - found submodules: %s", package_submodules)
    return package_submodules


# This function is called in an isolated sub-process via `isolated.Python.call`.
def _collect_submodules(name, on_error):
    import sys
    import pkgutil
    from traceback import format_exception_only

    from PyInstaller.utils.hooks import logger

    logger.debug("collect_submodules - scanning (sub)package %s", name)

    modules = []
    subpackages = []

    # Resolve package location(s)
    try:
        __import__(name)
    except Exception as ex:
        # Catch all errors and either raise, warn, or ignore them as determined by the *on_error* parameter.
        if on_error in ("warn", "warn once"):
            from PyInstaller.log import logger
            ex = "".join(format_exception_only(type(ex), ex)).strip()
            logger.warning(f"Failed to collect submodules for '{name}' because importing '{name}' raised: {ex}")
            if on_error == "warn once":
                on_error = "ignore"
            return modules, subpackages, on_error
        elif on_error == "raise":
            raise ImportError(f"Unable to load subpackage '{name}'.") from ex

    # Do not attempt to recurse into package if it did not make it into sys.modules.
    if name not in sys.modules:
        return modules, subpackages, on_error

    # Or if it does not have __path__ attribute.
    paths = getattr(sys.modules[name], '__path__', None) or []
    if not paths:
        return modules, subpackages, on_error

    # Package was successfully imported - include it in the list of modules.
    modules.append(name)

    # Iterate package contents
    logger.debug("collect_submodules - scanning (sub)package %s in location(s): %s", name, paths)
    for importer, name, ispkg in pkgutil.iter_modules(paths, name + '.'):
        if not ispkg:
            modules.append(name)
        else:
            subpackages.append(name)

    return modules, subpackages, on_error


def is_module_or_submodule(name: str, mod_or_submod: str):
    """
    This helper function is designed for use in the ``filter`` argument of :func:`collect_submodules`, by returning
    ``True`` if the given ``name`` is a module or a submodule of ``mod_or_submod``.

    Examples:

        The following excludes ``foo.test`` and ``foo.test.one`` but not ``foo.testifier``. ::

            collect_submodules('foo', lambda name: not is_module_or_submodule(name, 'foo.test'))``
    """
    return name.startswith(mod_or_submod + '.') or name == mod_or_submod


# Patterns of dynamic library filenames that might be bundled with some installed Python packages.
PY_DYLIB_PATTERNS = [
    '*.dll',
    '*.dylib',
    'lib*.so',
]


def collect_dynamic_libs(package: str, destdir: str | None = None, search_patterns: list = PY_DYLIB_PATTERNS):
    """
    This function produces a list of (source, dest) of dynamic library files that reside in package. Its output can be
    directly assigned to ``binaries`` in a hook script. The package parameter must be a string which names the package.

    :param destdir: Relative path to ./dist/APPNAME where the libraries should be put.
    :param search_patterns: List of dynamic library filename patterns to collect.
    """
    logger.debug('Collecting dynamic libraries for %s' % package)

    # Accept only strings as packages.
    if not isinstance(package, str):
        raise TypeError('package must be a str')

    # Skip a module which is not a package.
    if not is_package(package):
        logger.warning(
            "collect_dynamic_libs - skipping library collection for module '%s' as it is not a package.", package
        )
        return []

    pkg_dirs = get_all_package_paths(package)
    dylibs = []
    for pkg_dir in pkg_dirs:
        pkg_base = package_base_path(pkg_dir, package)
        # Recursively glob for all file patterns in the package directory
        for pattern in search_patterns:
            files = Path(pkg_dir).rglob(pattern)
            for source in files:
                # Produce the tuple ('/abs/path/to/source/mod/submod/file.pyd', 'mod/submod')
                if destdir:
                    # Put libraries in the specified target directory.
                    dest = destdir
                else:
                    # Preserve original directory hierarchy.
                    dest = source.parent.relative_to(pkg_base)
                logger.debug(' %s, %s' % (source, dest))
                dylibs.append((str(source), str(dest)))

    return dylibs


def collect_data_files(
    package: str,
    include_py_files: bool = False,
    subdir: str | os.PathLike | None = None,
    excludes: list | None = None,
    includes: list | None = None,
):
    r"""
    This function produces a list of ``(source, dest)`` entries for data files that reside in ``package``.
    Its output can be directly assigned to ``datas`` in a hook script; for example, see ``hook-sphinx.py``.
    The data files are all files that are not shared libraries / binary python extensions (based on extension
    check) and are not python source (.py) files or byte-compiled modules (.pyc). Collection of the .py and .pyc
    files can be toggled via the ``include_py_files`` flag.
    Parameters:

    -   The ``package`` parameter is a string which names the package.
    -   By default, python source files and byte-compiled modules (files with ``.py`` and ``.pyc`` suffix) are not
        collected; setting the ``include_py_files`` argument to ``True`` collects these files as well. This is typically
        used when a package requires source .py files to be available; for example, JIT compilation used in
        deep-learning frameworks, code that requires access to .py files (for example, to check their date), or code
        that tries to extend `sys.path` with subpackage paths in a way that is incompatible with PyInstaller's frozen
        importer.. However, in contemporary PyInstaller versions, the preferred way of collecting source .py files is by
        using the **module collection mode** setting (which enables collection of source .py files in addition to or
        in lieu of collecting byte-compiled modules into PYZ archive).
    -   The ``subdir`` argument gives a subdirectory relative to ``package`` to search, which is helpful when submodules
        are imported at run-time from a directory lacking ``__init__.py``.
    -   The ``excludes`` argument contains a sequence of strings or Paths. These provide a list of
        `globs <https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob>`_
        to exclude from the collected data files; if a directory matches the provided glob, all files it contains will
        be excluded as well. All elements must be relative paths, which are relative to the provided package's path
        (/ ``subdir`` if provided).

        Therefore, ``*.txt`` will exclude only ``.txt`` files in ``package``\ 's path, while ``**/*.txt`` will exclude
        all ``.txt`` files in ``package``\ 's path and all its subdirectories. Likewise, ``**/__pycache__`` will exclude
        all files contained in any subdirectory named ``__pycache__``.
    -   The ``includes`` function like ``excludes``, but only include matching paths. ``excludes`` override
        ``includes``: a file or directory in both lists will be excluded.

    This function does not work on zipped Python eggs.

    This function is intended to be used by hook scripts, not by main PyInstaller code.
    """
    logger.debug('Collecting data files for %s' % package)

    # Accept only strings as packages.
    if not isinstance(package, str):
        raise TypeError('package must be a str')

    # Skip a module which is not a package.
    if not is_package(package):
        logger.warning("collect_data_files - skipping data collection for module '%s' as it is not a package.", package)
        return []

    # Make sure the excludes are a list; this also makes a copy, so we don't modify the original.
    excludes = list(excludes) if excludes else []
    # These excludes may contain directories which need to be searched.
    excludes_len = len(excludes)
    # Including py files means don't exclude them. This pattern will search any directories for containing files, so
    # do not modify ``excludes_len``.
    if not include_py_files:
        excludes += ['**/*' + s for s in compat.ALL_SUFFIXES]
    else:
        # include_py_files should collect only .py and .pyc files, and not the extensions / shared libs.
        excludes += ['**/*' + s for s in compat.ALL_SUFFIXES if s not in {'.py', '.pyc'}]

    # Never, ever, collect .pyc files from __pycache__.
    excludes.append('**/__pycache__/*.pyc')

    # If not specified, include all files. Follow the same process as the excludes.
    includes = list(includes) if includes else ["**/*"]
    includes_len = len(includes)

    # A helper function to glob the in/ex "cludes", adding a wildcard to refer to all files under a subdirectory if a
    # subdirectory is matched by the first ``clude_len`` patterns. Otherwise, it in/excludes the matched file.
    # **This modifies** ``cludes``.
    def clude_walker(
        # Package directory to scan
        pkg_dir,
        # A list of paths relative to ``pkg_dir`` to in/exclude.
        cludes,
        # The number of ``cludes`` for which matching directories should be searched for all files under them.
        clude_len,
        # True if the list is includes, False for excludes.
        is_include
    ):
        for i, c in enumerate(cludes):
            for g in Path(pkg_dir).glob(c):
                if g.is_dir():
                    # Only files are sources. Subdirectories are not.
                    if i < clude_len:
                        # In/exclude all files under a matching subdirectory.
                        cludes.append(str((g / "**/*").relative_to(pkg_dir)))
                else:
                    # In/exclude a matching file.
                    sources.add(g) if is_include else sources.discard(g)

    # Obtain all paths for the specified package, and process each path independently.
    datas = []

    pkg_dirs = get_all_package_paths(package)
    for pkg_dir in pkg_dirs:
        sources = set()  # Reset sources set

        pkg_base = package_base_path(pkg_dir, package)
        if subdir:
            pkg_dir = os.path.join(pkg_dir, subdir)

        # Process the package path with clude walker
        clude_walker(pkg_dir, includes, includes_len, True)
        clude_walker(pkg_dir, excludes, excludes_len, False)

        # Transform the sources into tuples for ``datas``.
        datas += [(str(s), str(s.parent.relative_to(pkg_base))) for s in sources]

    logger.debug("collect_data_files - Found files: %s", datas)
    return datas


def collect_system_data_files(path: str, destdir: str | os.PathLike | None = None, include_py_files: bool = False):
    """
    This function produces a list of (source, dest) non-Python (i.e., data) files that reside somewhere on the system.
    Its output can be directly assigned to ``datas`` in a hook script.

    This function is intended to be used by hook scripts, not by main PyInstaller code.
    """
    # Accept only strings as paths.
    if not isinstance(path, str):
        raise TypeError('path must be a str')

    # Walk through all file in the given package, looking for data files.
    datas = []
    for dirpath, dirnames, files in os.walk(path):
        for f in files:
            extension = os.path.splitext(f)[1]
            if include_py_files or (extension not in PY_IGNORE_EXTENSIONS):
                # Produce the tuple: (/abs/path/to/source/mod/submod/file.dat, mod/submod/destdir)
                source = os.path.join(dirpath, f)
                dest = str(Path(dirpath).relative_to(path))
                if destdir is not None:
                    dest = os.path.join(destdir, dest)
                datas.append((source, dest))

    return datas


def copy_metadata(package_name: str, recursive: bool = False):
    """
    Collect distribution metadata so that ``importlib.metadata.distribution()`` or ``pkg_resources.get_distribution()``
    can find it.

    This function returns a list to be assigned to the ``datas`` global variable. This list instructs PyInstaller to
    copy the metadata for the given package to the frozen application's data directory.

    Parameters
    ----------
    package_name : str
        Specifies the name of the package for which metadata should be copied.
    recursive : bool
        If true, collect metadata for the package's dependencies too. This enables use of
        ``importlib.metadata.requires('package')`` or ``pkg_resources.require('package')`` inside the frozen
        application.

    Returns
    -------
    list
        This should be assigned to ``datas``.

    Examples
    --------
        >>> from PyInstaller.utils.hooks import copy_metadata
        >>> copy_metadata('sphinx')
        [('c:\\python27\\lib\\site-packages\\Sphinx-1.3.2.dist-info',
          'Sphinx-1.3.2.dist-info')]


    Some packages rely on metadata files accessed through the ``importlib.metadata`` (or the now-deprecated
    ``pkg_resources``) module. PyInstaller does not collect these metadata files by default.
    If a package fails without the metadata (either its own, or of another package that it depends on), you can use this
    function in a hook to collect the corresponding metadata files into the frozen application. The tuples in the
    returned list contain two strings. The first is the full path to the package's metadata directory on the system. The
    second is the destination name, which typically corresponds to the basename of the metadata directory. Adding these
    tuples the the ``datas`` hook global variable, the metadata is collected into top-level application directory (where
    it is usually searched for).

    .. versionchanged:: 4.3.1

        Prevent ``dist-info`` metadata folders being renamed to ``egg-info`` which broke ``pkg_resources.require`` with
        *extras* (see :issue:`#3033`).

    .. versionchanged:: 4.4.0

        Add the **recursive** option.
    """
    from collections import deque

    todo = deque([package_name])
    done = set()
    out = []

    while todo:
        package_name = todo.pop()
        if package_name in done:
            continue

        dist = importlib_metadata.distribution(package_name)

        # We support only `importlib_metadata.PathDistribution`, since we need to rely on its private `_path` attribute
        # to obtain the path to metadata file/directory. But we need to account for possible sub-classes and vendored
        # variants (`setuptools._vendor.importlib_metadata.PathDistribution˙), so just check that `_path` is available.
        if not hasattr(dist, '_path'):
            raise RuntimeError(
                f"Unsupported distribution type {type(dist)} for {package_name} - does not have _path attribute"
            )
        src_path = dist._path

        if src_path.is_dir():
            # The metadata is stored in a directory (.egg-info, .dist-info), so collect the whole directory. If the
            # package is installed as an egg, the metadata directory is ([...]/package_name-version.egg/EGG-INFO),
            # and requires special handling (as of PyInstaller v6, we support only non-zipped eggs).
            if src_path.name == 'EGG-INFO' and src_path.parent.name.endswith('.egg'):
                dest_path = os.path.join(*src_path.parts[-2:])
            else:
                dest_path = src_path.name
        elif src_path.is_file():
            # The metadata is stored in a single file. Collect it into top-level application directory.
            # The .egg-info file is commonly used by Debian/Ubuntu when packaging python packages.
            dest_path = '.'
        else:
            raise RuntimeError(
                f"Distribution metadata path {src_path!r} for {package_name} is neither file nor directory!"
            )

        out.append((str(src_path), str(dest_path)))

        if not recursive:
            return out
        done.add(package_name)

        # Process requirements; `importlib.metadata` has no API for parsing requirements, so we need to use
        # `packaging.requirements`. This is necessary to discard requirements with markers that do not match the
        # environment (e.g., `python_version`, `sys_platform`).
        requirements = [packaging.requirements.Requirement(req) for req in dist.requires or []]
        requirements = [req.name for req in requirements if req.marker is None or req.marker.evaluate()]

        todo += requirements

    return out


def get_installer(module: str):
    """
    Try to find which package manager installed a module.

    :param module: Module to check
    :return: Package manager or None
    """
    # Resolve distribution for given module/package name (e.g., enchant -> pyenchant).
    pkg_to_dist = importlib_metadata.packages_distributions()
    dist_names = pkg_to_dist.get(module)
    if dist_names is not None:
        # A namespace package might result in multiple dists; take the first one...
        try:
            dist = importlib_metadata.distribution(dist_names[0])
            installer_text = dist.read_text('INSTALLER')
            if installer_text is not None:
                return installer_text.strip()
        except importlib_metadata.PackageNotFoundError:
            # This might happen with eggs if the egg directory name does not match the dist name declared in the
            # metadata.
            pass

    if compat.is_darwin:
        try:
            file_name = get_module_file_attribute(module)
        except ImportError:
            return None

        # Attempt to resolve the module file via macports' port command
        try:
            output = subprocess.run(['port', 'provides', file_name],
                                    check=True,
                                    stdout=subprocess.PIPE,
                                    encoding='utf-8').stdout
            if 'is provided by' in output:
                return 'macports'
        except ExecCommandFailed:
            pass

        # Check if the file is located in homebrew's Cellar directory
        file_name = os.path.realpath(file_name)
        if 'Cellar' in file_name:
            return 'homebrew'

    return None


def collect_all(
    package_name: str,
    include_py_files: bool = True,
    filter_submodules: Callable = lambda name: True,
    exclude_datas: list | None = None,
    include_datas: list | None = None,
    on_error: str = "warn once",
):
    """
    Collect everything for a given package name.

    Arguments:
        package_name:
            An ``import``-able package name.
        include_py_files:
            Forwarded to :func:`collect_data_files`.
        filter_submodules:
            Forwarded to :func:`collect_submodules`.
        exclude_datas:
            Forwarded to :func:`collect_data_files`.
        include_datas:
            Forwarded to :func:`collect_data_files`.
        on_error:
            Forwarded onto :func:`collect_submodules`.

    Returns:
        tuple: A ``(datas, binaries, hiddenimports)`` triplet containing:

        - All data files, raw Python files (if **include_py_files**), and distribution metadata directories (if
          applicable).
        - All dynamic libraries as returned by :func:`collect_dynamic_libs`.
        - All submodules of **package_name**.

    Typical use::

        datas, binaries, hiddenimports = collect_all('my_package_name')
    """
    datas = collect_data_files(package_name, include_py_files, excludes=exclude_datas, includes=include_datas)
    binaries = collect_dynamic_libs(package_name)
    hiddenimports = collect_submodules(package_name, on_error=on_error, filter=filter_submodules)

    # `copy_metadata` requires a dist name instead of importable/package name.
    # A namespace package might belong to multiple distributions, so process all of them.
    pkg_to_dist = importlib_metadata.packages_distributions()
    dist_names = set(pkg_to_dist.get(package_name, []))
    for dist_name in dist_names:
        # Copy metadata
        try:
            datas += copy_metadata(dist_name)
        except Exception:
            pass

    return datas, binaries, hiddenimports


def collect_entry_point(name: str):
    """
    Collect modules and metadata for all exporters of a given entry point.

    Args:
        name:
            The name of the entry point. Check the documentation for the library that uses the entry point to find
            its name.
    Returns:
        A ``(datas, hiddenimports)`` pair that should be assigned to the ``datas`` and ``hiddenimports``, respectively.

    For libraries, such as ``pytest`` or ``keyring``, that rely on plugins to extend their behaviour.

    Examples:
        Pytest uses an entry point called ``'pytest11'`` for its extensions.
        To collect all those extensions use::

            datas, hiddenimports = collect_entry_point("pytest11")

        These values may be used in a hook or added to the ``datas`` and ``hiddenimports`` arguments in the ``.spec``
        file. See :ref:`using spec files`.

    .. versionadded:: 4.3
    """
    datas = []
    imports = []
    for entry_point in importlib_metadata.entry_points(group=name):
        datas += copy_metadata(entry_point.dist.name)
        imports.append(entry_point.module)
    return datas, imports


def get_hook_config(hook_api: PostGraphAPI, module_name: str, key: str):
    """
    Get user settings for hooks.

    Args:
        module_name:
            The module/package for which the key setting belong to.
        key:
            A key for the config.
    Returns:
        The value for the config. ``None`` if not set.

    The ``get_hook_config`` function will lookup settings in the ``Analysis.hooksconfig`` dict.

    The hook settings can be added to ``.spec`` file in the form of::

        a = Analysis(["my-app.py"],
            ...
            hooksconfig = {
                "gi": {
                    "icons": ["Adwaita"],
                    "themes": ["Adwaita"],
                    "languages": ["en_GB", "zh_CN"],
                },
            },
            ...
        )
    """
    config = hook_api.analysis.hooksconfig
    value = None
    if module_name in config and key in config[module_name]:
        value = config[module_name][key]
    return value


def include_or_exclude_file(
    filename: str,
    include_list: list | None = None,
    exclude_list: list | None = None,
):
    """
    Generic inclusion/exclusion decision function based on filename and list of include and exclude patterns.

    Args:
        filename:
            Filename considered for inclusion.
        include_list:
            List of inclusion file patterns.
        exclude_list:
            List of exclusion file patterns.

    Returns:
        A boolean indicating whether the file should be included or not.

    If ``include_list`` is provided, True is returned only if the filename matches one of include patterns (and does not
    match any patterns in ``exclude_list``, if provided). If ``include_list`` is not provided, True is returned if
    filename does not match any patterns in ``exclude list``, if provided. If neither list is provided, True is
    returned for any filename.
    """
    if include_list is not None:
        for pattern in include_list:
            if fnmatch.fnmatch(filename, pattern):
                break
        else:
            return False  # Not explicitly included; exclude

    if exclude_list is not None:
        for pattern in exclude_list:
            if fnmatch.fnmatch(filename, pattern):
                return False  # Explicitly excluded

    return True


def collect_delvewheel_libs_directory(package_name, libdir_name=None, datas=None, binaries=None):
    """
    Collect data files and binaries from the .libs directory of a delvewheel-enabled python wheel. Such wheels ship
    their shared libraries in a .libs directory that is located next to the package directory, and therefore falls
    outside the purview of the collect_dynamic_libs() utility function.

    Args:
        package_name:
            Name of the package (e.g., scipy).
        libdir_name:
            Optional name of the .libs directory (e.g., scipy.libs). If not provided, ".libs" is added to
            ``package_name``.
        datas:
            Optional list of datas to which collected data file entries are added. The combined result is retuned
            as part of the output tuple.
        binaries:
            Optional list of binaries to which collected binaries entries are added. The combined result is retuned
            as part of the output tuple.

    Returns:
        tuple: A ``(datas, binaries)`` pair that should be assigned to the ``datas`` and ``binaries``, respectively.

    Examples:
        Collect the ``scipy.libs`` delvewheel directory belonging to the Windows ``scipy`` wheel::

            datas, binaries = collect_delvewheel_libs_directory("scipy")

        When the collected entries should be added to existing ``datas`` and ``binaries`` listst, the following form
        can be used to avoid using intermediate temporary variables and merging those into existing lists::

            datas, binaries = collect_delvewheel_libs_directory("scipy", datas=datas, binaries=binaries)

    .. versionadded:: 5.6
    """

    datas = datas or []
    binaries = binaries or []

    if libdir_name is None:
        libdir_name = package_name + '.libs'

    # delvewheel is applicable only to Windows wheels
    if not compat.is_win:
        return datas, binaries

    # Get package's parent path
    pkg_base, pkg_dir = get_package_paths(package_name)
    pkg_base = Path(pkg_base)
    libs_dir = pkg_base / libdir_name

    if not libs_dir.is_dir():
        return datas, binaries

    # Collect all dynamic libs - collect them as binaries in order to facilitate proper binary dependency analysis
    # (for example, to ensure that system-installed VC runtime DLLs are collected, if needed).
    # As of PyInstaller 5.4, this should be safe (should not result in duplication), because binary dependency
    # analysis attempts to preserve the DLL directory structure.
    binaries += [(str(dll_file), str(dll_file.parent.relative_to(pkg_base))) for dll_file in libs_dir.glob('*.dll')]

    # Collect the .load-order file; strictly speaking, this should be necessary only under python < 3.8, but let us
    # collect it for completeness sake. Differently named variants have been observed: `.load_order`, `.load-order`,
    # and `.load-order-Name`.
    datas += [(str(load_order_file), str(load_order_file.parent.relative_to(pkg_base)))
              for load_order_file in libs_dir.glob('.load[-_]order*')]

    return datas, binaries


if compat.is_pure_conda:
    from PyInstaller.utils.hooks import conda as conda_support  # noqa: F401
elif compat.is_conda:
    from PyInstaller.utils.hooks.conda import CONDA_META_DIR as _tmp
    logger.warning(
        "Assuming this is not an Anaconda environment or an additional venv/pipenv/... environment manager is being "
        "used on top, because the conda-meta folder %s does not exist.", _tmp
    )
    del _tmp
