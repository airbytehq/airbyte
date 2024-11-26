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

from PyInstaller.utils.hooks import can_import_module, collect_data_files, is_module_satisfies

datas = collect_data_files('sudachipy')
hiddenimports = []

# In v0.6.8, `sudachipy.config` and `sudachipy.errors` modules were added, and are referenced from binary extension.
if is_module_satisfies('sudachipy >= 0.6.8'):
    hiddenimports += [
        'sudachipy.config',
        'sudachipy.errors',
    ]

# Check which types of dictionary are installed
for sudachi_dict in ['sudachidict_small', 'sudachidict_core', 'sudachidict_full']:
    if can_import_module(sudachi_dict):
        datas += collect_data_files(sudachi_dict)

        hiddenimports += [sudachi_dict]
