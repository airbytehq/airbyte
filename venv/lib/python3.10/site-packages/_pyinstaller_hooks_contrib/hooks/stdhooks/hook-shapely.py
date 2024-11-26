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

import os
from ctypes.util import find_library

from PyInstaller.utils.hooks import get_package_paths
from PyInstaller.utils.hooks import is_module_satisfies
from PyInstaller import compat

# Necessary when using the vectorized subpackage
hiddenimports = ['shapely.prepared']

if is_module_satisfies('shapely >= 2.0.0'):
    # An import made in the `shapely.geometry_helpers` extension; both `shapely.geometry_helpers` and `shapely._geos`
    # extensions were introduced in v2.0.0.
    hiddenimports += ['shapely._geos']

pkg_base, pkg_dir = get_package_paths('shapely')

binaries = []
datas = []
if compat.is_win:
    geos_c_dll_found = False

    # Search conda directory if conda is active, then search standard
    # directory. This is the same order of precidence used in shapely.
    standard_path = os.path.join(pkg_dir, 'DLLs')
    lib_paths = [standard_path, os.environ['PATH']]
    if compat.is_conda:
        conda_path = os.path.join(compat.base_prefix, 'Library', 'bin')
        lib_paths.insert(0, conda_path)
    original_path = os.environ['PATH']
    try:
        os.environ['PATH'] = os.pathsep.join(lib_paths)
        dll_path = find_library('geos_c')
    finally:
        os.environ['PATH'] = original_path
    if dll_path is not None:
        binaries += [(dll_path, '.')]
        geos_c_dll_found = True

    # Starting with shapely 1.8.1, the DLLs shipped with PyPI wheels are stored in
    # site-packages/Shapely.libs instead of sub-directory in site-packages/shapely.
    if is_module_satisfies("shapely >= 1.8.1"):
        lib_dir = os.path.join(pkg_base, "Shapely.libs")
        if os.path.isdir(lib_dir):
            # We collect DLLs as data files instead of binaries to suppress binary
            # analysis, which would result in duplicates (because it collects a copy
            # into the top-level directory instead of preserving the original layout).
            # In addition to DLls, this also collects .load-order* file (required on
            # python < 3.8), and ensures that Shapely.libs directory exists (required
            # on python >= 3.8 due to os.add_dll_directory call).
            datas += [
                (os.path.join(lib_dir, lib_file), 'Shapely.libs')
                for lib_file in os.listdir(lib_dir)
            ]

            geos_c_dll_found |= any([
                os.path.basename(lib_file).startswith("geos_c")
                for lib_file, _ in datas
            ])

    if not geos_c_dll_found:
        raise SystemExit(
            "Error: geos_c.dll not found, required by hook-shapely.py.\n"
            "Please check your installation or provide a pull request to "
            "PyInstaller to update hook-shapely.py.")
elif compat.is_linux and is_module_satisfies('shapely < 1.7'):
    # This duplicates the libgeos*.so* files in the build.  PyInstaller will
    # copy them into the root of the build by default, but shapely cannot load
    # them from there in linux IF shapely was installed via a whl file. The
    # whl bundles its own libgeos with a different name, something like
    # libgeos_c-*.so.* but shapely tries to load libgeos_c.so if there isn't a
    # ./libs directory under its package.
    #
    # The fix for this (https://github.com/Toblerity/Shapely/pull/485) has
    # been available in shapely since version 1.7.
    lib_dir = os.path.join(pkg_dir, '.libs')
    dest_dir = os.path.join('shapely', '.libs')

    binaries += [(os.path.join(lib_dir, f), dest_dir) for f in os.listdir(lib_dir)]
elif compat.is_darwin and is_module_satisfies('shapely >= 1.8.1'):
    # In shapely 1.8.1, the libgeos_c library bundled in macOS PyPI wheels is not
    # called libgeos.1.dylib anymore, but rather has a fullly-versioned name
    # (e.g., libgeos_c.1.16.0.dylib).
    # Shapely fails to find such a library unless it is located in the .dylibs
    # directory. So we need to ensure that the libraries are collected into
    # .dylibs directory; however, this will result in duplication due to binary
    # analysis of the python extensions that are linked against these libraries
    # as well (as that will copy the libraries to top-level directory).
    lib_dir = os.path.join(pkg_dir, '.dylibs')
    dest_dir = os.path.join('shapely', '.dylibs')

    if os.path.isdir(lib_dir):
        binaries += [(os.path.join(lib_dir, f), dest_dir) for f in os.listdir(lib_dir)]
