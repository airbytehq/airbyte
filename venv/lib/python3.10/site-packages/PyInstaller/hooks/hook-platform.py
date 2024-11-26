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
import sys

# see https://github.com/python/cpython/blob/3.9/Lib/platform.py#L411
# This will exclude `plistlib` for sys.platform != 'darwin'
if sys.platform != 'darwin':
    excludedimports = ["plistlib"]
