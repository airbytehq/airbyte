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

# pywin32 supports frozen mode; in that mode, it is looking at sys.path for pythoncomXY.dll. However, as of
# PyInstaller 5.4, we may collect that DLL into its original pywin32_system32 sub-directory as part of the
# binary dependency analysis (and add it to sys.path by means of a runtime hook).

import pathlib

from PyInstaller.utils.hooks import is_module_satisfies, get_pywin32_module_file_attribute

dll_filename = get_pywin32_module_file_attribute('pythoncom')
dst_dir = '.'  # Top-level application directory

if is_module_satisfies('PyInstaller >= 5.4'):
    # Try preserving the original pywin32_system directory, if applicable (it is not applicable in Anaconda,
    # where the DLL is located in Library/bin).
    dll_path = pathlib.Path(dll_filename)
    if dll_path.parent.name == 'pywin32_system32':
        dst_dir = 'pywin32_system32'

binaries = [(dll_filename, dst_dir)]
