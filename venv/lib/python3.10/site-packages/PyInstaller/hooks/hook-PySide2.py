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

from PyInstaller.utils.hooks.qt import pyside2_library_info

# Only proceed if PySide2 can be imported.
if pyside2_library_info.version is not None:
    hiddenimports = ['shiboken2', 'inspect']
    if pyside2_library_info.version < [5, 15]:
        # The shiboken2 bootstrap in earlier releases requires __future__ in addition to inspect
        hiddenimports += ['__future__']

    # Collect required Qt binaries.
    binaries = pyside2_library_info.collect_extra_binaries()
