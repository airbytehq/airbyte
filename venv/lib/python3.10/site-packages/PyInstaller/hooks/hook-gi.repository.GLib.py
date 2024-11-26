#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

import glob
import os

from PyInstaller.compat import is_win
from PyInstaller.utils.hooks import get_hook_config
from PyInstaller.utils.hooks.gi import GiModuleInfo, collect_glib_share_files, collect_glib_translations


def hook(hook_api):
    module_info = GiModuleInfo('GLib', '2.0')
    if not module_info.available:
        return

    binaries, datas, hiddenimports = module_info.collect_typelib_data()

    # Collect translations
    lang_list = get_hook_config(hook_api, "gi", "languages")
    datas += collect_glib_translations('glib20', lang_list)

    # Collect schemas
    datas += collect_glib_share_files('glib-2.0', 'schemas')

    # On Windows, glib needs a spawn helper for g_spawn* API
    if is_win:
        pattern = os.path.join(module_info.get_libdir(), 'gspawn-*-helper*.exe')
        for f in glob.glob(pattern):
            binaries.append((f, '.'))

    hook_api.add_datas(datas)
    hook_api.add_binaries(binaries)
    hook_api.add_imports(*hiddenimports)
