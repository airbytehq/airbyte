# ------------------------------------------------------------------
# Copyright (c) 2022 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import is_module_satisfies, collect_submodules

hiddenimports = []

# Required by scikit-learn 1.0.0
if is_module_satisfies("scikit-learn >= 1.0.0"):
    hiddenimports += [
        'sklearn.utils._typedefs',
    ]

# Required by scikit-learn 1.2.0
if is_module_satisfies("scikit-learn >= 1.2.0"):
    hiddenimports += collect_submodules("sklearn.metrics._pairwise_distances_reduction")
