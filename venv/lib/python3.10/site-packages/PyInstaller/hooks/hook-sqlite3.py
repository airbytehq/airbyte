#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []

# On Windows in Python 3.4 'sqlite3' package might contain tests that are not required in frozen application.
for mod in collect_submodules('sqlite3'):
    if not mod.startswith('sqlite3.test'):
        hiddenimports.append(mod)
