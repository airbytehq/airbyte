# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
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
import glob

from PyInstaller.utils.hooks import get_module_file_attribute
from PyInstaller.compat import is_win

# blspy comes as a stand-alone extension module that's placed directly
# in site-packages.
#
# On macOS and Linux, it is linked against the GMP library, whose shared
# library is stored in blspy.libs and .dylibsblspy, respectively. As this
# is a linked dependency, it is collected properly by PyInstaller and
# no further work is needed.
#
# On Windows, however, the blspy extension is linked against MPIR library,
# whose DLLs are placed directly into site-packages. The mpir.dll is
# linked dependency and is picked up automatically, but it in turn
# dynamically loads CPU-specific backends that are named mpir_*.dll.
# We need to colllect these manually.
if is_win:
    blspy_dir = os.path.dirname(get_module_file_attribute('blspy'))
    mpir_dlls = glob.glob(os.path.join(blspy_dir, 'mpir_*.dll'))
    binaries = [(mpir_dll, '.') for mpir_dll in mpir_dlls]
