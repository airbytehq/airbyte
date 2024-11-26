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
import sys
from PyInstaller.utils.hooks import collect_data_files, is_module_satisfies, copy_metadata
from PyInstaller.compat import is_win, is_conda

hiddenimports = [
    "pyproj.datadir"
]

# Versions prior to 2.3.0 also require pyproj._datadir
if not is_module_satisfies("pyproj >= 2.3.0"):
    hiddenimports += ["pyproj._datadir"]

# Starting with version 3.0.0, pyproj._compat is needed
if is_module_satisfies("pyproj >= 3.0.0"):
    hiddenimports += ["pyproj._compat"]
    # Linux and macOS also require distutils.
    if not is_win:
        hiddenimports += ["distutils.util"]

# Data collection
datas = collect_data_files('pyproj')

if hasattr(sys, 'real_prefix'):  # check if in a virtual environment
    root_path = sys.real_prefix
else:
    root_path = sys.prefix

# - conda-specific
if is_win:
    tgt_proj_data = os.path.join('Library', 'share', 'proj')
    src_proj_data = os.path.join(root_path, 'Library', 'share', 'proj')

else:  # both linux and darwin
    tgt_proj_data = os.path.join('share', 'proj')
    src_proj_data = os.path.join(root_path, 'share', 'proj')

if is_conda:
    if os.path.exists(src_proj_data):
        datas.append((src_proj_data, tgt_proj_data))
    else:
        from PyInstaller.utils.hooks import logger
        logger.warning("Datas for pyproj not found at:\n{}".format(src_proj_data))
    # A runtime hook defines the path for `PROJ_LIB`

# With pyproj 3.4.0, we need to collect package's metadata due to `importlib.metadata.version(__package__)` call in
# `__init__.py`. This change was reverted in subsequent releases of pyproj, so we collect metadata only for 3.4.0.
if is_module_satisfies("pyproj == 3.4.0"):
    datas += copy_metadata("pyproj")
