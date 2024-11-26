# ------------------------------------------------------------------
# Copyright (c) 2022 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import os

from PyInstaller.utils.hooks import get_module_attribute, logger
from PyInstaller.depend.utils import _resolveCtypesImports

binaries = []

# Use the _LIB_NAME attribute of discid.libdiscid to resolve the shared library name. This saves us from having to
# duplicate the name guessing logic from discid.libdiscid.
# On error, PyInstaller >= 5.0 raises exception, earlier versions return an empty string.
try:
    lib_name = get_module_attribute("discid.libdiscid", "_LIB_NAME")
except Exception:
    lib_name = None

if lib_name:
    lib_name = os.path.basename(lib_name)
    try:
        resolved_binary = _resolveCtypesImports([lib_name])
        lib_file = resolved_binary[0][1]
    except Exception as e:
        lib_file = None
        logger.warning("Error while trying to resolve %s: %s", lib_name, e)

    if lib_file:
        binaries += [(lib_file, '.')]
else:
    logger.warning("Failed to determine name of libdiscid shared library from _LIB_NAME attribute of discid.libdiscid!")
