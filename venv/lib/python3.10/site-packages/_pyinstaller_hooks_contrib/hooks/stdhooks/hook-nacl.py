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

# Tested with PyNaCl 0.3.0 on Mac OS X.

import os.path
import glob

from PyInstaller.compat import EXTENSION_SUFFIXES
from PyInstaller.utils.hooks import collect_data_files, get_module_file_attribute

datas = collect_data_files('nacl')

# Include the cffi extensions as binaries in a subfolder named like the package.
binaries = []
nacl_dir = os.path.dirname(get_module_file_attribute('nacl'))
for ext in EXTENSION_SUFFIXES:
    ffimods = glob.glob(os.path.join(nacl_dir, '_lib', '*_cffi_*%s*' % ext))
    dest_dir = os.path.join('nacl', '_lib')
    for f in ffimods:
        binaries.append((f, dest_dir))
