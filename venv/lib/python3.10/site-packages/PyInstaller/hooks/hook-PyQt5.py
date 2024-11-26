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

from PyInstaller.utils.hooks.qt import pyqt5_library_info

# Only proceed if PyQt5 can be imported.
if pyqt5_library_info.version is not None:
    hiddenimports = [
        # PyQt5.10 and earlier uses sip in an separate package;
        'sip',
        # PyQt5.11 and later provides SIP in a private package. Support both.
        'PyQt5.sip',
        # Imported via __import__ in PyQt5/__init__.py
        'pkgutil',
    ]

    # Collect required Qt binaries.
    binaries = pyqt5_library_info.collect_extra_binaries()
