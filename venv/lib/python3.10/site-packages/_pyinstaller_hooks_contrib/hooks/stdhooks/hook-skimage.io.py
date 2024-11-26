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

# This hook was tested with scikit-image (skimage) 0.14.1:
# https://scikit-image.org

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("skimage.io._plugins")
hiddenimports = collect_submodules('skimage.io._plugins')
