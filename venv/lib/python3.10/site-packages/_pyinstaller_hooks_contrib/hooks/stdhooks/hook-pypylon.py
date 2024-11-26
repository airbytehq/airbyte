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

# PyPylon is a tricky library to bundle. It encapsulates the pylon C++ SDK inside
# it with modified library references to make the module relocatable.
# PyInstaller is able to find those libraries and preserve the linkage for almost
# all of them. However - there is an additional linking step happening at runtime,
# when the library is creating the transport layer for the camera. This linking
# will fail with the library files modified by pyinstaller.
# As the module is already relocatable, we circumvent this issue by bundling
# pypylon as-is - for pyinstaller we treat the shared library files as just data.

import os

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs

# Collect dynamic libs as data (to prevent pyinstaller from modifying them)
datas = collect_dynamic_libs('pypylon')

# Collect data files, looking for pypylon/pylonCXP/bin/ProducerCXP.cti, but other files may also be needed
datas += collect_data_files('pypylon')

# Exclude the C++-extensions from automatic search, add them manually as data files
# their dependencies were already handled with collect_dynamic_libs
excludedimports = ['pypylon._pylon', 'pypylon._genicam']
for filename, module in collect_data_files('pypylon', include_py_files=True):
    if (os.path.basename(filename).startswith('_pylon.')
            or os.path.basename(filename).startswith('_genicam.')):
        datas += [(filename, module)]
