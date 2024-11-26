#-----------------------------------------------------------------------------
# Copyright (c) 2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller import compat

# Up until python 3.12, `xxsubtype` was built-in on all OSes. Now it is an extension on non-Windows, and without it,
# shiboken6 initialization segfaults.
if compat.is_py312 and not compat.is_win:
    hiddenimports = ['xxsubtype']
