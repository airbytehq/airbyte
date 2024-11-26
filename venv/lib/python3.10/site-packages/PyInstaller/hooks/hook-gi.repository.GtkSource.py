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

from PyInstaller.utils.hooks.gi import GiModuleInfo, collect_glib_share_files


def hook(hook_api):
    module_info = GiModuleInfo('GtkSource', '3.0', hook_api=hook_api)  # Pass hook_api to read version from hook config
    if not module_info.available:
        return

    binaries, datas, hiddenimports = module_info.collect_typelib_data()

    # Collect data files
    # The data directory name contains verbatim version, e.g.:
    #   * GtkSourceView-3.0 -> /usr/share/gtksourceview-3.0
    #   * GtkSourceView-4 -> /usr/share/gtksourceview-4
    #   * GtkSourceView-5 -> /usr/share/gtksourceview-5
    datas += collect_glib_share_files(f'gtksourceview-{module_info.version}')

    hook_api.add_datas(datas)
    hook_api.add_binaries(binaries)
    hook_api.add_imports(*hiddenimports)
