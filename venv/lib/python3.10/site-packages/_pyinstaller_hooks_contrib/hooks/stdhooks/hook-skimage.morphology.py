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

from PyInstaller.utils.hooks import collect_data_files, is_module_satisfies

# As of scikit-image 0.20.0, we need to collect .npy data files for `skimage.morphology`
if is_module_satisfies('scikit-image >= 0.20'):
    datas = collect_data_files("skimage.morphology", includes=["*.npy"])
