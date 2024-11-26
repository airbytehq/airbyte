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

from PyInstaller.utils.hooks import can_import_module, copy_metadata, collect_data_files

datas = copy_metadata('pymorphy3_dicts_ru')
datas += collect_data_files('pymorphy3_dicts_ru')

hiddenimports = ['pymorphy3_dicts_ru']

# Check if the Ukrainian model is installed
if can_import_module('pymorphy3_dicts_uk'):
    datas += copy_metadata('pymorphy3_dicts_uk')
    datas += collect_data_files('pymorphy3_dicts_uk')

    hiddenimports += ['pymorphy3_dicts_uk']
