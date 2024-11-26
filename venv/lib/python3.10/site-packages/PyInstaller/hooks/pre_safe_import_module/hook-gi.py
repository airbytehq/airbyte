#-----------------------------------------------------------------------------
# Copyright (c) 2022-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller import compat
from PyInstaller.utils import hooks as hookutils


def pre_safe_import_module(api):
    if compat.is_linux:
        # RHEL/Fedora RPM package for GObject introspection is known to split the `gi` package into two locations:
        #  - /usr/lib64/python3.x/site-packages/gi
        #  - /usr/lib/python3.x/site-packages/gi
        # The `__init__.py` is located in the first directory, while `repository` and `overrides` are located in
        # the second, and `__init__.py` dynamically extends the `__path__` during package import, using
        #  `__path__ = pkgutil.extend_path(__path__, __name__)`.
        # The modulegraph has no way of knowing this, so we need extend the package path in this hook. Otherwise,
        # only the first location is scanned, and the `gi.repository` ends up missing.
        #
        # NOTE: the `get_package_paths`/`get_package_all_paths` helpers read the paths from package's spec without
        # importing the (top-level) package, so they do not catch run-time path modifications. Instead, we use
        # `get_module_attribute` to import the package in isolated process and query its `__path__` attribute.
        try:
            paths = hookutils.get_module_attribute(api.module_name, "__path__")
        except Exception:
            # Most likely `gi` cannot be imported.
            paths = []

        for path in paths:
            api.append_package_path(path)
