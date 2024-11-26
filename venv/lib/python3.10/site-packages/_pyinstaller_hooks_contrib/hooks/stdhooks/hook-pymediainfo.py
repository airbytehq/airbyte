# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.compat import is_win, is_darwin
from PyInstaller.utils.hooks import collect_dynamic_libs, logger

# Collect bundled mediainfo shared library (available in Windows and macOS wheels on PyPI).
binaries = collect_dynamic_libs("pymediainfo")

# On linux, no wheels are available, and pymediainfo uses system shared library.
if not binaries and not (is_win or is_darwin):

    def _find_system_mediainfo_library():
        import os
        import ctypes.util
        from PyInstaller.depend.utils import _resolveCtypesImports

        libname = ctypes.util.find_library("mediainfo")
        if libname is not None:
            resolved_binary = _resolveCtypesImports([os.path.basename(libname)])
            if resolved_binary:
                return resolved_binary[0][1]

    try:
        mediainfo_lib = _find_system_mediainfo_library()
    except Exception as e:
        logger.warning("Error while trying to find system-installed MediaInfo library: %s", e)
        mediainfo_lib = None

    if mediainfo_lib:
        # Put the library into pymediainfo sub-directory, to keep layout consistent with that of wheels.
        binaries += [(mediainfo_lib, 'pymediainfo')]

if not binaries:
    logger.warning("MediaInfo shared library not found - pymediainfo will likely fail to work!")
