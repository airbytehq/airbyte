#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

# To make pkg_resources work with frozen modules we need to set the 'Provider' class for PyiFrozenImporter. This class
# decides where to look for resources and other stuff. 'pkg_resources.NullProvider' is dedicated to PEP302 import hooks
# like PyiFrozenImporter is. It uses method __loader__.get_data() in methods pkg_resources.resource_string() and
# pkg_resources.resource_stream()
#
# We provide PyiFrozenProvider, which subclasses the NullProvider and implements _has(), _isdir(), and _listdir()
# methods, which are needed for pkg_resources.resource_exists(), resource_isdir(), and resource_listdir() to work. We
# cannot use the DefaultProvider, because it provides filesystem-only implementations (and overrides _get() with a
# filesystem-only one), whereas our provider needs to also support embedded resources.
#
# The PyiFrozenProvider allows querying/listing both PYZ-embedded and on-filesystem resources in a frozen package. The
# results are typically combined for both types of resources (e.g., when listing a directory or checking whether a
# resource exists). When the order of precedence matters, the PYZ-embedded resources take precedence over the
# on-filesystem ones, to keep the behavior consistent with the actual file content retrieval via _get() method (which in
# turn uses PyiFrozenImporter's get_data() method). For example, when checking whether a resource is a directory via
# _isdir(), a PYZ-embedded file will take precedence over a potential on-filesystem directory. Also, in contrast to
# unfrozen packages, the frozen ones do not contain source .py files, which are therefore absent from content listings.


def _pyi_rthook():
    import os
    import pathlib
    import sys

    import pkg_resources
    from pyimod02_importers import PyiFrozenImporter

    SYS_PREFIX = pathlib.PurePath(sys._MEIPASS)

    class _TocFilesystem:
        """
        A prefix tree implementation for embedded filesystem reconstruction.

        NOTE: as of PyInstaller 6.0, the embedded PYZ archive cannot contain data files anymore. Instead, it contains
        only .pyc modules - which are by design not returned by `PyiFrozenProvider`. So this implementation has been
        reduced to supporting only directories implied by collected packages.
        """
        def __init__(self, tree_node):
            self._tree = tree_node

        def _get_tree_node(self, path):
            path = pathlib.PurePath(path)
            current = self._tree
            for component in path.parts:
                if component not in current:
                    return None
                current = current[component]
            return current

        def path_exists(self, path):
            node = self._get_tree_node(path)
            return isinstance(node, dict)  # Directory only

        def path_isdir(self, path):
            node = self._get_tree_node(path)
            return isinstance(node, dict)  # Directory only

        def path_listdir(self, path):
            node = self._get_tree_node(path)
            if not isinstance(node, dict):
                return []  # Non-existent or file
            # Return only sub-directories
            return [entry_name for entry_name, entry_data in node.items() if isinstance(entry_data, dict)]

    class PyiFrozenProvider(pkg_resources.NullProvider):
        """
        Custom pkg_resources provider for PyiFrozenImporter.
        """
        def __init__(self, module):
            super().__init__(module)

            # Get top-level path; if "module" corresponds to a package, we need the path to the package itself.
            # If "module" is a submodule in a package, we need the path to the parent package.
            #
            # This is equivalent to `pkg_resources.NullProvider.module_path`, except we construct a `pathlib.PurePath`
            # for easier manipulation.
            #
            # NOTE: the path is NOT resolved for symbolic links, as neither are paths that are passed by `pkg_resources`
            # to `_has`, `_isdir`, `_listdir` (they are all anchored to `module_path`, which in turn is just
            # `os.path.dirname(module.__file__)`. As `__file__` returned by `PyiFrozenImporter` is always anchored to
            # `sys._MEIPASS`, we do not have to worry about cross-linked directories in macOS .app bundles, where the
            # resolved `__file__` could be either in the `Contents/Frameworks` directory (the "true" `sys._MEIPASS`), or
            # in the `Contents/Resources` directory due to cross-linking.
            self._pkg_path = pathlib.PurePath(module.__file__).parent

            # Construct _TocFilesystem on top of pre-computed prefix tree provided by PyiFrozenImporter.
            self.embedded_tree = _TocFilesystem(self.loader.toc_tree)

        def _normalize_path(self, path):
            # Avoid using `Path.resolve`, because it resolves symlinks. This is undesirable, because the pure path in
            # `self._pkg_path` does not have symlinks resolved, so comparison between the two would be faulty. Instead,
            # use `os.path.normpath` to normalize the path and get rid of any '..' elements (the path itself should
            # already be absolute).
            return pathlib.Path(os.path.normpath(path))

        def _is_relative_to_package(self, path):
            return path == self._pkg_path or self._pkg_path in path.parents

        def _has(self, path):
            # Prevent access outside the package.
            path = self._normalize_path(path)
            if not self._is_relative_to_package(path):
                return False

            # Check the filesystem first to avoid unnecessarily computing the relative path...
            if path.exists():
                return True
            rel_path = path.relative_to(SYS_PREFIX)
            return self.embedded_tree.path_exists(rel_path)

        def _isdir(self, path):
            # Prevent access outside the package.
            path = self._normalize_path(path)
            if not self._is_relative_to_package(path):
                return False

            # Embedded resources have precedence over filesystem...
            rel_path = path.relative_to(SYS_PREFIX)
            node = self.embedded_tree._get_tree_node(rel_path)
            if node is None:
                return path.is_dir()  # No match found; try the filesystem.
            else:
                # str = file, dict = directory
                return not isinstance(node, str)

        def _listdir(self, path):
            # Prevent access outside the package.
            path = self._normalize_path(path)
            if not self._is_relative_to_package(path):
                return []

            # Relative path for searching embedded resources.
            rel_path = path.relative_to(SYS_PREFIX)
            # List content from embedded filesystem...
            content = self.embedded_tree.path_listdir(rel_path)
            # ... as well as the actual one.
            if path.is_dir():
                # Use os.listdir() to avoid having to convert Path objects to strings... Also make sure to de-duplicate
                # the results.
                path = str(path)  # not is_py36
                content = list(set(content + os.listdir(path)))
            return content

    pkg_resources.register_loader_type(PyiFrozenImporter, PyiFrozenProvider)


_pyi_rthook()
del _pyi_rthook
