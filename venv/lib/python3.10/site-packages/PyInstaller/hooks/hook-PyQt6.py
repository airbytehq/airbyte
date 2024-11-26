#-----------------------------------------------------------------------------
# Copyright (c) 2021-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.utils.hooks.qt import pyqt6_library_info

# Only proceed if PyQt6 can be imported.
if pyqt6_library_info.version is not None:
    hiddenimports = [
        'PyQt6.sip',
        # Imported via __import__ in PyQt6/__init__.py
        'pkgutil',
    ]

    # Collect required Qt binaries.
    binaries = pyqt6_library_info.collect_extra_binaries()
