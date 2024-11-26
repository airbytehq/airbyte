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

from PyInstaller.utils.hooks import is_module_satisfies

# sklearn.cluster in scikit-learn 0.23.x has a hidden import of
# threadpoolctl
if is_module_satisfies("scikit_learn >= 0.23"):
    hiddenimports = ['threadpoolctl', ]
