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

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect core plugins.
hiddenimports = collect_submodules('hydra._internal.core_plugins')

# Collect package's data files, such as default configuration files.
datas = collect_data_files('hydra')
