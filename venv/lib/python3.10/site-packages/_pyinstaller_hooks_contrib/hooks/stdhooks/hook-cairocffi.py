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
import ctypes.util
import os

from PyInstaller.depend.utils import _resolveCtypesImports
from PyInstaller.utils.hooks import collect_data_files, is_module_satisfies, logger

datas = collect_data_files("cairocffi")

binaries = []

# NOTE: Update this if cairocffi requires more libraries
libs = ["cairo-2", "cairo", "libcairo-2"]

try:
    lib_basenames = []
    for lib in libs:
        libname = ctypes.util.find_library(lib)
        if libname is not None:
            lib_basenames += [os.path.basename(libname)]

    if lib_basenames:
        resolved_libs = _resolveCtypesImports(lib_basenames)
        for resolved_lib in resolved_libs:
            binaries.append((resolved_lib[1], '.'))
except Exception as e:
    logger.warning("Error while trying to find system-installed Cairo library: %s", e)

if not binaries:
    logger.warning("Cairo library not found - cairocffi will likely fail to work!")

# cairocffi 1.6.0 requires cairocffi/constants.py source file, so make sure it is collected.
# The module collection mode setting requires PyInstaller >= 5.3.
if is_module_satisfies('cairocffi >= 1.6.0'):
    module_collection_mode = {'cairocffi.constants': 'pyz+py'}
