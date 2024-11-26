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

from PyInstaller.utils.hooks import is_module_satisfies, collect_data_files, collect_submodules

# The following missing module prevents import of skimage.feature with skimage 0.17.x.
hiddenimports = ['skimage.feature._orb_descriptor_positions', ]

# Collect the data file with ORB descriptor positions. In earlier versions of scikit-image, this file was in
# `skimage/data` directory, and it was moved to `skimage/feature` in v0.17.0. Collect if from wherever it is.
datas = collect_data_files('skimage', includes=['**/orb_descriptor_positions.txt'])

# As of scikit-image 0.22.0, we need to collect the __init__.pyi file for `lazy_loader`, as well as collect submodules
# due to lazy loading.
if is_module_satisfies("scikit-image >= 0.22.0"):
    datas += collect_data_files("skimage.feature", includes=["*.pyi"])
    hiddenimports = collect_submodules('skimage.feature', filter=lambda name: name != 'skimage.feature.tests')
