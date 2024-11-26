# -----------------------------------------------------------------------------
# Copyright (c) 2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------
"""
This hook allows discovery and collection of PyInstaller's internal _pyi_rth_utils module that provides utility
functions for run-time hooks.

The module is implemented in 'PyInstaller/fake-modules/_pyi_rth_utils.py'.
"""

import os

from PyInstaller import PACKAGEPATH


def pre_find_module_path(api):
    module_dir = os.path.join(PACKAGEPATH, 'fake-modules')
    api.search_dirs = [module_dir]
