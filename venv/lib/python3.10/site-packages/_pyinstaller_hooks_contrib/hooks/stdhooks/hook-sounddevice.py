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
sounddevice:
https://github.com/spatialaudio/python-sounddevice/
"""

import pathlib

from PyInstaller.utils.hooks import get_module_file_attribute, logger

binaries = []
datas = []

# PyPI wheels for Windows and macOS ship the sndfile shared library in _sounddevice_data directory,
# located next to the sounddevice.py module file (i.e., in the site-packages directory).
module_dir = pathlib.Path(get_module_file_attribute('sounddevice')).parent
data_dir = module_dir / '_sounddevice_data' / 'portaudio-binaries'
if data_dir.is_dir():
    destdir = str(data_dir.relative_to(module_dir))

    # Collect the shared library (known variants: libportaudio64bit.dll, libportaudio32bit.dll, libportaudio.dylib)
    for lib_file in data_dir.glob("libportaudio*.*"):
        binaries += [(str(lib_file), destdir)]

    # Collect the README.md file
    readme_file = data_dir / "README.md"
    if readme_file.is_file():
        datas += [(str(readme_file), destdir)]
else:
    # On linux and in Anaconda in all OSes, the system-installed portaudio library needs to be collected.
    def _find_system_portaudio_library():
        import os
        import ctypes.util
        from PyInstaller.depend.utils import _resolveCtypesImports

        libname = ctypes.util.find_library("portaudio")
        if libname is not None:
            resolved_binary = _resolveCtypesImports([os.path.basename(libname)])
            if resolved_binary:
                return resolved_binary[0][1]

    try:
        lib_file = _find_system_portaudio_library()
    except Exception as e:
        logger.warning("Error while trying to find system-installed portaudio library: %s", e)
        lib_file = None

    if lib_file:
        binaries += [(lib_file, '.')]

if not binaries:
    logger.warning("portaudio shared library not found - sounddevice will likely fail to work!")
