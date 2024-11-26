# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
"""
pysoundfile:
https://github.com/bastibe/SoundFile
"""

import pathlib

from PyInstaller.utils.hooks import get_module_file_attribute, logger

binaries = []
datas = []

# PyPI wheels for Windows and macOS ship the sndfile shared library in _soundfile_data directory,
# located next to the soundfile.py module file (i.e., in the site-packages directory).
module_dir = pathlib.Path(get_module_file_attribute('soundfile')).parent
data_dir = module_dir / '_soundfile_data'
if data_dir.is_dir():
    destdir = str(data_dir.relative_to(module_dir))

    # Collect the shared library (known variants: libsndfile64bit.dll, libsndfile32bit.dll, libsndfile.dylib)
    for lib_file in data_dir.glob("libsndfile*.*"):
        binaries += [(str(lib_file), destdir)]

    # Collect the COPYING file
    copying_file = data_dir / "COPYING"
    if copying_file.is_file():
        datas += [(str(copying_file), destdir)]
else:
    # On linux and in Anaconda in all OSes, the system-installed sndfile library needs to be collected.
    def _find_system_sndfile_library():
        import os
        import ctypes.util
        from PyInstaller.depend.utils import _resolveCtypesImports

        libname = ctypes.util.find_library("sndfile")
        if libname is not None:
            resolved_binary = _resolveCtypesImports([os.path.basename(libname)])
            if resolved_binary:
                return resolved_binary[0][1]

    try:
        lib_file = _find_system_sndfile_library()
    except Exception as e:
        logger.warning("Error while trying to find system-installed sndfile library: %s", e)
        lib_file = None

    if lib_file:
        binaries += [(lib_file, '.')]

if not binaries:
    logger.warning("sndfile shared library not found - soundfile will likely fail to work!")
