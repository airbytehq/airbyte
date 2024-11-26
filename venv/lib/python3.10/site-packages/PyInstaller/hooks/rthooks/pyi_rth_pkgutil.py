#-----------------------------------------------------------------------------
# Copyright (c) 2021-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------
#
# This rthook overrides pkgutil.iter_modules with custom implementation that uses PyInstaller's PyiFrozenImporter to
# list sub-modules embedded in the PYZ archive. The non-embedded modules (binary extensions, or .pyc modules in
# noarchive build) are handled by original pkgutil iter_modules implementation (and consequently, python's FileFinder).
#
# The preferred way of adding support for iter_modules would be adding non-standard iter_modules() method to
# PyiFrozenImporter itself. However, that seems to work only for path entry finders (for use with sys.path_hooks), while
# PyInstaller's PyiFrozenImporter is registered as meta path finders (for use with sys.meta_path). Turning
# PyiFrozenImporter into path entry finder, would seemingly require the latter to support on-filesystem resources
# (e.g., extension modules) in addition to PYZ-embedded ones.
#
# Therefore, we instead opt for overriding pkgutil.iter_modules with custom implementation that augments the output of
# original implementation with contents of PYZ archive from PyiFrozenImporter's TOC.


def _pyi_rthook():
    import pathlib
    import pkgutil
    import sys

    from pyimod02_importers import PyiFrozenImporter
    from _pyi_rth_utils import is_macos_app_bundle

    _orig_pkgutil_iter_modules = pkgutil.iter_modules

    def _pyi_pkgutil_iter_modules(path=None, prefix=''):
        # Use original implementation to discover on-filesystem modules (binary extensions in regular builds, or both
        # binary extensions and compiled pyc modules in noarchive debug builds).
        yield from _orig_pkgutil_iter_modules(path, prefix)

        # Find the instance of PyInstaller's PyiFrozenImporter.
        for importer in pkgutil.iter_importers():
            if isinstance(importer, PyiFrozenImporter):
                break
        else:
            return

        if path is None:
            # Search for all top-level packages/modules in the PyiFrozenImporter's prefix tree.
            for entry_name, entry_data in importer.toc_tree.items():
                # Package nodes have dict for data, module nodes (leaves) have (empty) strings.
                is_pkg = isinstance(entry_data, dict)
                yield pkgutil.ModuleInfo(importer, prefix + entry_name, is_pkg)
        else:
            # Fully resolve sys._MEIPASS, in order to avoid path mis-matches when the given search paths also contain
            # symbolic links and are already fully resolved. See #6537 for an example of such a problem with onefile
            # build on macOS, where the temporary directory is placed under /var, which is actually a symbolic link
            # to /private/var.
            MEIPASS = pathlib.Path(sys._MEIPASS).resolve()

            # For macOS .app bundles, the "true" sys._MEIPASS is `name.app/Contents/Frameworks`, but due to
            # cross-linking, we must also consider `name.app/Contents/Resources`. See #7884.
            if is_macos_app_bundle:
                ALT_MEIPASS = (pathlib.Path(sys._MEIPASS).parent / "Resources").resolve()

            # Process all given paths
            seen_pkg_prefices = set()
            for pkg_path in path:
                # Fully resolve the given path, in case it contains symbolic links.
                pkg_path = pathlib.Path(pkg_path).resolve()

                # Try to compute package prefix, which is the remainder of the given path, relative to the sys._MEIPASS.
                pkg_prefix = None
                try:
                    pkg_prefix = pkg_path.relative_to(MEIPASS)
                except ValueError:  # ValueError: 'a' is not in the subpath of 'b'
                    pass

                # For macOS .app bundle, try the alternative sys._MEIPASS
                if pkg_prefix is None and is_macos_app_bundle:
                    try:
                        pkg_prefix = pkg_path.relative_to(ALT_MEIPASS)
                    except ValueError:
                        pass

                # Given path is outside of sys._MEIPASS; ignore it.
                if pkg_prefix is None:
                    continue

                # If we are given multiple paths and they are either duplicated or resolve to the same package prefix,
                # prevent duplication.
                if pkg_prefix in seen_pkg_prefices:
                    continue
                seen_pkg_prefices.add(pkg_prefix)

                # Traverse the PyiFrozenImporter's prefix tree using components of the relative package path, starting
                # at the tree root. This implicitly handles the case where the given path was actually sys._MEIPASS
                # itself, as in this case pkg_prefix is pathlib.Path(".") with empty parts tuple.
                tree_node = importer.toc_tree
                for pkg_name_part in pkg_prefix.parts:
                    tree_node = tree_node.get(pkg_name_part)
                    if tree_node is None:
                        tree_node = {}
                        break

                # List entries from the target node.
                for entry_name, entry_data in tree_node.items():
                    is_pkg = isinstance(entry_data, dict)
                    yield pkgutil.ModuleInfo(importer, prefix + entry_name, is_pkg)

    pkgutil.iter_modules = _pyi_pkgutil_iter_modules


_pyi_rthook()
del _pyi_rthook
