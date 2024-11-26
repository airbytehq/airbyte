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

import pathlib

from PyInstaller import compat
from PyInstaller.utils.hooks import collect_dynamic_libs, get_installer, get_package_paths


# Query the installer of the `rtree` package; in PyInstaller prior to 6.0, this might raise an exception, whereas in
# later versions, None is returned.
try:
    package_installer = get_installer('rtree')
except Exception:
    package_installer = None

if package_installer == 'conda':
    from PyInstaller.utils.hooks import conda

    # In Anaconda-packaged `rtree`, `libspatialindex` and `libspatialindex_c` shared libs are packaged in a separate
    # `libspatialindex` package. Collect the libraries into `rtree/lib` sub-directory to simulate PyPI wheel layout.
    binaries = conda.collect_dynamic_libs('libspatialindex', dest='rtree/lib', dependencies=False)
else:
    # pip-installed package. The shared libs are usually placed in `rtree/lib` directory.
    binaries = collect_dynamic_libs('rtree')

    # With rtree >= 1.1.0, Linux PyPI wheels place the shared library in a `Rtree.libs` top-level directory.
    if compat.is_linux:
        _, rtree_dir = get_package_paths('rtree')
        rtree_libs_dir = pathlib.Path(rtree_dir).parent / 'Rtree.libs'
        binaries += [(str(lib_file), 'Rtree.libs') for lib_file in rtree_libs_dir.glob("libspatialindex*.so*")]
