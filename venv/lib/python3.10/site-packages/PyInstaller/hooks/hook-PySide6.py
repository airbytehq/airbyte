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

from PyInstaller.utils.hooks import check_requirement
from PyInstaller.utils.hooks.qt import pyside6_library_info

# Only proceed if PySide6 can be imported.
if pyside6_library_info.version is not None:
    hiddenimports = ['shiboken6', 'inspect']

    # Starting with PySide6 6.4.0, we need to collect PySide6.support.deprecated for | and & operators to work with
    # Qt key and key modifiers enums. See #7249.
    if check_requirement("PySide6 >= 6.4.0"):
        hiddenimports += ['PySide6.support.deprecated']

    # Collect required Qt binaries.
    binaries = pyside6_library_info.collect_extra_binaries()
