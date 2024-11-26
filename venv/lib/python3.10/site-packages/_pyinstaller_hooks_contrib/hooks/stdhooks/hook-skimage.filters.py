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

from PyInstaller.utils.hooks import is_module_satisfies, collect_data_files, collect_submodules

if is_module_satisfies("scikit-image >= 0.19.0"):
    # In scikit-image 0.19.x, `skimage.filters` switched to lazy module loading, so we need to collect all submodules.
    hiddenimports = collect_submodules('skimage.filters', filter=lambda name: name != 'skimage.filters.tests')

    # In scikit-image 0.20.0, `lazy_loader` is used, so we need to collect `__init__.pyi` file.
    if is_module_satisfies("scikit-image >= 0.20.0"):
        datas = collect_data_files("skimage.filters", includes=["*.pyi"])
elif is_module_satisfies("scikit-image >= 0.18.0"):
    # The following missing module prevents import of skimage.feature with skimage 0.18.x.
    hiddenimports = ['skimage.filters.rank.core_cy_3d', ]
