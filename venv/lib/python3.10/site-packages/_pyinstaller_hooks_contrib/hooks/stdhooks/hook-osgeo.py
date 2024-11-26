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

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.compat import is_win, is_darwin

import os
import sys

# The osgeo libraries require auxiliary data and may have hidden dependencies.
# There are several possible configurations on how these libraries can be
# deployed.
# This hook evaluates the cases when:
# - the `data` folder is present "in-source" (sharing the same namespace folder
#   as the code libraries)
# - the `data` folder is present "out-source" (for instance, on Anaconda for
#   Windows, in PYTHONHOME/Library/data)
# In this latter case, the hook also checks for the presence of `proj` library
# (e.g., on Windows in PYTHONHOME) for being added to the bundle.
#
# This hook has been tested with gdal (v.1.11.2 and 1.11.3) on:
# - Win 7 and 10 64bit
# - Ubuntu 15.04 64bit
# - Mac OS X Yosemite 10.10
#
# TODO: Fix for gdal>=2.0.0, <2.0.3: 'NameError: global name 'help' is not defined'

# flag used to identify an Anaconda environment
is_conda = False

# Auxiliary data:
#
# - general case (data in 'osgeo/data/gdal'):
datas = collect_data_files('osgeo', subdir=os.path.join('data', 'gdal'))

# check if the data has been effectively found in 'osgeo/data/gdal'
if len(datas) == 0:

    if hasattr(sys, 'real_prefix'):  # check if in a virtual environment
        root_path = sys.real_prefix
    else:
        root_path = sys.prefix

    # - conda-specific
    if is_win:
        tgt_gdal_data = os.path.join('Library', 'share', 'gdal')
        src_gdal_data = os.path.join(root_path, 'Library', 'share', 'gdal')
        if not os.path.exists(src_gdal_data):
            tgt_gdal_data = os.path.join('Library', 'data')
            src_gdal_data = os.path.join(root_path, 'Library', 'data')

    else:  # both linux and darwin
        tgt_gdal_data = os.path.join('share', 'gdal')
        src_gdal_data = os.path.join(root_path, 'share', 'gdal')

    if os.path.exists(src_gdal_data):
        is_conda = True
        datas.append((src_gdal_data, tgt_gdal_data))
        # a real-time hook takes case to define the path for `GDAL_DATA`

# Hidden dependencies
if is_conda:
    # if `proj.4` is present, it provides additional functionalities
    if is_win:
        proj4_lib = os.path.join(root_path, 'proj.dll')
    elif is_darwin:
        proj4_lib = os.path.join(root_path, 'lib', 'libproj.dylib')
    else:  # assumed linux-like settings
        proj4_lib = os.path.join(root_path, 'lib', 'libproj.so')

    if os.path.exists(proj4_lib):
        binaries = [(proj4_lib, ".")]
