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

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from the package. These include:
#  - package's and subpackages' .pyi files for `lazy_loader`
#  - example data in librosa/util, required by `librosa.util.files`
#  - librosa/core/intervals.msgpack, required by `librosa.core.intervals`
#
# We explicitly exclude `__pycache__` because it might contain .nbi and .nbc files from `numba` cache, which are not
# re-used by `numba` codepaths in the frozen application and are instead re-compiled in user-global cache directory.
datas = collect_data_files("librosa", excludes=['**/__pycache__'])

# And because modules are lazily loaded, we need to collect them all.
hiddenimports = collect_submodules("librosa")
