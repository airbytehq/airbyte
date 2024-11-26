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

# language=rst
"""
Additional helper methods for working specifically with Anaconda distributions are found at
:mod:`PyInstaller.utils.hooks.conda_support<PyInstaller.utils.hooks.conda>`
which is designed to mimic (albeit loosely) the `importlib.metadata`_ package. These functions find and parse the
distribution metadata from json files located in the ``conda-meta`` directory.

.. versionadded:: 4.2.0

This module is available only if run inside a Conda environment. Usage of this module should therefore be wrapped in
a conditional clause::

    from PyInstaller.compat import is_pure_conda

    if is_pure_conda:
        from PyInstaller.utils.hooks import conda_support

        # Code goes here. e.g.
        binaries = conda_support.collect_dynamic_libs("numpy")
        ...

Packages are all referenced by the *distribution name* you use to install it, rather than the *package name* you import
it with. I.e., use ``distribution("pillow")`` instead of ``distribution("PIL")`` or use ``package_distribution("PIL")``.
"""
from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path
from typing import Iterable, List
from importlib.metadata import PackagePath as _PackagePath

from PyInstaller import compat
from PyInstaller.log import logger

# Conda virtual environments each get their own copy of `conda-meta` so the use of `sys.prefix` instead of
# `sys.base_prefix`, `sys.real_prefix` or anything from our `compat` module is intentional.
CONDA_ROOT = Path(sys.prefix)
CONDA_META_DIR = CONDA_ROOT / "conda-meta"

# Find all paths in `sys.path` that are inside Conda root.
PYTHONPATH_PREFIXES = []
for _path in sys.path:
    _path = Path(_path)
    try:
        PYTHONPATH_PREFIXES.append(_path.relative_to(sys.prefix))
    except ValueError:
        pass

PYTHONPATH_PREFIXES.sort(key=lambda p: len(p.parts), reverse=True)


class Distribution:
    """
    A bucket class representation of a Conda distribution.

    This bucket exports the following attributes:

    :ivar name: The distribution's name.
    :ivar version: Its version.
    :ivar files: All filenames as :meth:`PackagePath`\\ s included with this distribution.
    :ivar dependencies: Names of other distributions that this distribution depends on (with version constraints
                        removed).
    :ivar packages: Names of importable packages included in this distribution.

    This class is not intended to be constructed directly by users. Rather use :meth:`distribution` or
    :meth:`package_distribution` to provide one for you.
    """
    def __init__(self, json_path: str):
        try:
            self._json_path = Path(json_path)
            assert self._json_path.exists()
        except (TypeError, AssertionError):
            raise TypeError(
                "Distribution requires a path to a conda-meta json. Perhaps you want "
                "`distribution({})` instead?".format(repr(json_path))
            )

        # Everything we need (including this distribution's name) is kept in the metadata json.
        self.raw: dict = json.loads(self._json_path.read_text())

        # Unpack the more useful contents of the json.
        self.name: str = self.raw["name"]
        self.version: str = self.raw["version"]
        self.files = [PackagePath(i) for i in self.raw["files"]]
        self.dependencies = self._init_dependencies()
        self.packages = self._init_package_names()

    def __repr__(self):
        return "{}(name=\"{}\", packages={})".format(type(self).__name__, self.name, self.packages)

    def _init_dependencies(self):
        """
        Read dependencies from ``self.raw["depends"]``.

        :return: Dependent distribution names.
        :rtype: list

        The names in ``self.raw["depends"]`` come with extra version constraint information which must be stripped.
        """
        dependencies = []
        # For each dependency:
        for dependency in self.raw["depends"]:
            # ``dependency`` is a string of the form: "[name] [version constraints]"
            name, *version_constraints = dependency.split(maxsplit=1)
            dependencies.append(name)
        return dependencies

    def _init_package_names(self):
        """
        Search ``self.files`` for package names shipped by this distribution.

        :return: Package names.
        :rtype: list

        These are names you would ``import`` rather than names you would install.
        """
        packages = []
        for file in self.files:
            package = _get_package_name(file)
            if package is not None:
                packages.append(package)
        return packages

    @classmethod
    def from_name(cls, name: str):
        """
        Get distribution information for a given distribution **name** (i.e., something you would ``conda install``).

        :rtype: :class:`Distribution`
        """
        if name in distributions:
            return distributions[name]
        raise ModuleNotFoundError(
            "Distribution {} is either not installed or was not installed using Conda.".format(name)
        )

    @classmethod
    def from_package_name(cls, name: str):
        """
        Get distribution information for a **package** (i.e., something you would import).

        :rtype: :class:`Distribution`

        For example, the package ``pkg_resources`` belongs to the distribution ``setuptools``, which contains three
        packages.

        >>> package_distribution("pkg_resources")
        Distribution(name="setuptools",
                     packages=['easy_install', 'pkg_resources', 'setuptools'])
        """
        if name in distributions_by_package:
            return distributions_by_package[name]
        raise ModuleNotFoundError("Package {} is either not installed or was not installed using Conda.".format(name))


distribution = Distribution.from_name
package_distribution = Distribution.from_package_name


class PackagePath(_PackagePath):
    """
    A filename relative to Conda's root (``sys.prefix``).

    This class inherits from :class:`pathlib.PurePosixPath` even on non-Posix OSs. To convert to a :class:`pathlib.Path`
    pointing to the real file, use the :meth:`locate` method.
    """
    def locate(self):
        """
        Return a path-like object for this path pointing to the file's true location.
        """
        return Path(sys.prefix) / self


def walk_dependency_tree(initial: str, excludes: Iterable[str] | None = None):
    """
    Collect a :class:`Distribution` and all direct and indirect dependencies of that distribution.

    Arguments:
        initial:
            Distribution name to collect from.
        excludes:
            Distributions to exclude.
    Returns:
        A ``{name: distribution}`` mapping where ``distribution`` is the output of
        :func:`conda_support.distribution(name) <distribution>`.
    """
    if excludes is not None:
        excludes = set(excludes)

    # Rather than use true recursion, mimic it with a to-do queue.
    from collections import deque
    done = {}
    names_to_do = deque([initial])

    while names_to_do:
        # Grab a distribution name from the to-do list.
        name = names_to_do.pop()
        try:
            # Collect and save it's metadata.
            done[name] = distribution = Distribution.from_name(name)
            logger.debug("Collected Conda distribution '%s', a dependency of '%s'.", name, initial)
        except ModuleNotFoundError:
            logger.warning(
                "Conda distribution '%s', dependency of '%s', was not found. "
                "If you installed this distribution with pip then you may ignore this warning.", name, initial
            )
            continue
        # For each dependency:
        for _name in distribution.dependencies:
            if _name in done:
                # Skip anything already done.
                continue
            if _name == name:
                # Avoid infinite recursion if a distribution depends on itself. This will probably never happen but I
                # certainly would not chance it.
                continue
            if excludes is not None and _name in excludes:
                # Do not recurse to excluded dependencies.
                continue
            names_to_do.append(_name)
    return done


def _iter_distributions(name, dependencies, excludes):
    if dependencies:
        return walk_dependency_tree(name, excludes).values()
    else:
        return [Distribution.from_name(name)]


def requires(name: str, strip_versions: bool = False) -> List[str]:
    """
    List requirements of a distribution.

    Arguments:
        name:
            The name of the distribution.
        strip_versions:
            List only their names, not their version constraints.
    Returns:
        A list of distribution names.
    """
    if strip_versions:
        return distribution(name).dependencies
    return distribution(name).raw["depends"]


def files(name: str, dependencies: bool = False, excludes: list | None = None) -> List[PackagePath]:
    """
    List all files belonging to a distribution.

    Arguments:
        name:
            The name of the distribution.
        dependencies:
            Recursively collect files of dependencies too.
        excludes:
            Distributions to ignore if **dependencies** is true.
    Returns:
        All filenames belonging to the given distribution.

    With ``dependencies=False``, this is just a shortcut for::

        conda_support.distribution(name).files
    """
    return [file for dist in _iter_distributions(name, dependencies, excludes) for file in dist.files]


if compat.is_win:
    lib_dir = PackagePath("Library", "bin")
else:
    lib_dir = PackagePath("lib")


def collect_dynamic_libs(name: str, dest: str = ".", dependencies: bool = True, excludes: Iterable[str] | None = None):
    """
    Collect DLLs for distribution **name**.

    Arguments:
        name:
            The distribution's project-name.
        dest:
            Target destination, defaults to ``'.'``.
        dependencies:
            Recursively collect libs for dependent distributions (recommended).
        excludes:
            Dependent distributions to skip, defaults to ``None``.
    Returns:
        List of DLLs in PyInstaller's ``(source, dest)`` format.

    This collects libraries only from Conda's shared ``lib`` (Unix) or ``Library/bin`` (Windows) folders. To collect
    from inside a distribution's installation use the regular :func:`PyInstaller.utils.hooks.collect_dynamic_libs`.
    """
    DLL_SUFFIXES = ("*.dll", "*.dylib", "*.so", "*.so.*")
    _files = []
    for file in files(name, dependencies, excludes):
        # A file is classified as a dynamic library if:
        #  1) it lives inside the dedicated ``lib_dir`` DLL folder
        if file.parent != lib_dir:
            continue
        #  2) it is a file (and not a directory or a symbolic link pointing to a directory)
        resolved_file = file.locate()
        if not resolved_file.is_file():
            continue
        #  3) has a correct suffix
        if not any([resolved_file.match(suffix) for suffix in DLL_SUFFIXES]):
            continue

        _files.append((str(resolved_file), dest))
    return _files


# --- Map packages to distributions and vice-versa ---


def _get_package_name(file: PackagePath):
    """
    Determine the package name of a Python file in :data:`sys.path`.

    Arguments:
        file:
            A Python filename relative to Conda root (sys.prefix).
    Returns:
        Package name or None.

    This function only considers single file packages e.g. ``foo.py`` or top level ``foo/__init__.py``\\ s.
    Anything else is ignored (returning ``None``).
    """
    file = Path(file)
    # TODO: Handle PEP 420 namespace packages (which are missing `__init__` module). No such Conda PEP 420 namespace
    # packages are known.

    # Get top-level folders by finding parents of `__init__.xyz`s
    if file.stem == "__init__" and file.suffix in compat.ALL_SUFFIXES:
        file = file.parent
    elif file.suffix not in compat.ALL_SUFFIXES:
        # Keep single-file packages but skip DLLs, data and junk files.
        return

    # Check if this file/folder's parent is in ``sys.path`` i.e. it's directly importable. This intentionally excludes
    # submodules which would cause confusion because ``sys.prefix`` is in ``sys.path``, meaning that every file in an
    # Conda installation is a submodule.
    for prefix in PYTHONPATH_PREFIXES:
        if len(file.parts) != len(prefix.parts) + 1:
            # This check is redundant but speeds it up quite a bit.
            continue
        # There are no wildcards involved here. The use of ``fnmatch`` is simply to handle the `if case-insensitive
        # file system: use case-insensitive string matching.`
        if fnmatch.fnmatch(str(file.parent), str(prefix)):
            return file.stem


# All the information we want is organised the wrong way.

# We want to look up distribution based on package names, but we can only search for packages using distribution names.
# And we would like to search for a distribution's json file, but, due to the noisy filenames of the jsons, we can only
# find a json's distribution rather than a distribution's json.

# So we have to read everything, then regroup distributions in the ways we want them grouped. This will likely be a
# spectacular bottleneck on full-blown Conda (non miniconda) with 250+ packages by default at several GiBs. I suppose we
# could cache this on a per-json basis if it gets too much.


def _init_distributions():
    distributions = {}
    for path in CONDA_META_DIR.glob("*.json"):
        dist = Distribution(path)
        distributions[dist.name] = dist
    return distributions


distributions = _init_distributions()


def _init_packages():
    distributions_by_package = {}
    for distribution in distributions.values():
        for package in distribution.packages:
            distributions_by_package[package] = distribution
    return distributions_by_package


distributions_by_package = _init_packages()
