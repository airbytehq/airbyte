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

# Required by scikit-learn 0.21
from PyInstaller.utils.hooks import is_module_satisfies

if is_module_satisfies("scikit-learn < 0.22"):
    hiddenimports = [
        'sklearn.utils.lgamma',
        'sklearn.utils.weight_vector'
    ]
else:
    # lgamma was removed and weight_vector privatised in 0.22.
    # https://github.com/scikit-learn/scikit-learn/commit/58be9a671b0b8fcb4b75f4ae99f4469ca33a2158#diff-dbca16040fd2b85a499ba59833b37f1785c58e52d2e89ce5cdfc7fff164bd5f3
    # https://github.com/scikit-learn/scikit-learn/commit/150e82b52bf28c88c5a8b1a10f9777d0452b3ef2
    hiddenimports = [
        'sklearn.utils._weight_vector'
    ]
