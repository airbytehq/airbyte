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

from PyInstaller.utils.hooks import is_module_satisfies

# sklearn.linear_model in scikit-learn 0.24.x has a hidden import of
# sklearn.utils._weight_vector
if is_module_satisfies("scikit_learn >= 0.24"):
    hiddenimports = ['sklearn.utils._weight_vector', ]
