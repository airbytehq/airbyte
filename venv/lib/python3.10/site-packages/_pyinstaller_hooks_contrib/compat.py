# ------------------------------------------------------------------
# Copyright (c) 2023 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import sys

from PyInstaller.utils.hooks import is_module_satisfies


if is_module_satisfies("PyInstaller >= 6.0"):
    # PyInstaller >= 6.0 imports importlib_metadata in its compat module
    from PyInstaller.compat import importlib_metadata
else:
    # Older PyInstaller version - duplicate logic from PyInstaller 6.0
    class ImportlibMetadataError(SystemExit):
        def __init__(self):
            super().__init__(
                "pyinstaller-hooks-contrib requires importlib.metadata from python >= 3.10 stdlib or "
                "importlib_metadata from importlib-metadata >= 4.6"
            )

    if sys.version_info >= (3, 10):
        import importlib.metadata as importlib_metadata
    else:
        try:
            import importlib_metadata
        except ImportError as e:
            raise ImportlibMetadataError() from e

        import packaging.version  # For importlib_metadata version check

        # Validate the version
        if packaging.version.parse(importlib_metadata.version("importlib-metadata")) < packaging.version.parse("4.6"):
            raise ImportlibMetadataError()
