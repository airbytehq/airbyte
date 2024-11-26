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
Hook for https://github.com/libtcod/python-tcod
"""
from PyInstaller.utils.hooks import collect_dynamic_libs

hiddenimports = ['_cffi_backend']

# Install shared libraries to the working directory.
binaries = collect_dynamic_libs('tcod', destdir='.')
