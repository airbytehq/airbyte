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

# Hook for imageio: http://imageio.github.io/

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('imageio', subdir="resources")

# imageio plugins are imported lazily since ImageIO version 2.11.0.
# They are very light-weight, so we can safely include all of them.
hiddenimports = collect_submodules('imageio.plugins')
