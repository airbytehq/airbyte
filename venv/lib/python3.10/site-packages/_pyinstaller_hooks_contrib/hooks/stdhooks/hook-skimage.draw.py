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

from PyInstaller.utils.hooks import is_module_satisfies, collect_data_files, collect_submodules

# As of scikit-image 0.21.0, we need to collect the __init__.pyi file for `lazy_loader`, as well as collect submodules
# due to lazy loading.
if is_module_satisfies("scikit-image >= 0.21.0"):
    datas = collect_data_files("skimage.draw", includes=["*.pyi"])
    hiddenimports = collect_submodules('skimage.draw', filter=lambda name: name != 'skimage.draw.tests')
