# ------------------------------------------------------------------
# Copyright (c) 2023 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
import os

from PyInstaller.compat import is_win
from PyInstaller.utils.hooks import get_package_paths

# In all versions for which fastparquet provides Windows wheels (>= 0.7.0), delvewheel is used,
# so we need to collect the external site-packages/fastparquet.libs directory.
if is_win:
    pkg_base, pkg_dir = get_package_paths("fastparquet")
    lib_dir = os.path.join(pkg_base, "fastparquet.libs")
    if os.path.isdir(lib_dir):
        # We collect DLLs as data files instead of binaries to suppress binary
        # analysis, which would result in duplicates (because it collects a copy
        # into the top-level directory instead of preserving the original layout).
        # In addition to DLls, this also collects .load-order* file (required on
        # python < 3.8), and ensures that fastparquet.libs directory exists (required
        # on python >= 3.8 due to os.add_dll_directory call).
        datas = [
            (os.path.join(lib_dir, lib_file), 'fastparquet.libs')
            for lib_file in os.listdir(lib_dir)
        ]
