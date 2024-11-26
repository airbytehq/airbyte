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

# GStreamer contains a lot of plugins. We need to collect them and bundle them with the exe file. We also need to
# resolve binary dependencies of these GStreamer plugins.

import pathlib

from PyInstaller.utils.hooks import get_hook_config, include_or_exclude_file
import PyInstaller.log as logging
from PyInstaller import isolated
from PyInstaller.utils.hooks.gi import GiModuleInfo, collect_glib_share_files, collect_glib_translations

logger = logging.getLogger(__name__)


@isolated.decorate
def _get_gst_plugin_path():
    import os
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    reg = Gst.Registry.get()
    plug = reg.find_plugin('coreelements')
    path = plug.get_filename()
    return os.path.dirname(path)


def _format_plugin_pattern(plugin_name):
    return f"**/*gst{plugin_name}.*"


def hook(hook_api):
    module_info = GiModuleInfo('Gst', '1.0')
    if not module_info.available:
        return

    binaries, datas, hiddenimports = module_info.collect_typelib_data()
    hiddenimports += ["gi.repository.Gio"]

    # Collect data files
    datas += collect_glib_share_files('gstreamer-1.0')

    # Translations
    lang_list = get_hook_config(hook_api, "gi", "languages")
    for prog in [
        'gst-plugins-bad-1.0',
        'gst-plugins-base-1.0',
        'gst-plugins-good-1.0',
        'gst-plugins-ugly-1.0',
        'gstreamer-1.0',
    ]:
        datas += collect_glib_translations(prog, lang_list)

    # Plugins
    try:
        plugin_path = _get_gst_plugin_path()
    except Exception as e:
        logger.warning("Failed to determine gstreamer plugin path: %s", e)
        plugin_path = None

    if plugin_path:
        plugin_path = pathlib.Path(plugin_path)

        # Obtain optional include/exclude list from hook config
        include_list = get_hook_config(hook_api, "gstreamer", "include_plugins")
        exclude_list = get_hook_config(hook_api, "gstreamer", "exclude_plugins")

        # Format plugin basenames into filename patterns for matching
        if include_list is not None:
            include_list = [_format_plugin_pattern(name) for name in include_list]
        if exclude_list is not None:
            exclude_list = [_format_plugin_pattern(name) for name in exclude_list]

        # The names of GStreamer plugins typically start with libgst (or just gst, depending on the toolchain). We also
        # need to account for different extensions that might be used on a particular OS (for example, on macOS, the
        # extension may be either .so or .dylib).
        for lib_pattern in ['*gst*.dll', '*gst*.dylib', '*gst*.so']:
            binaries += [(str(filename), 'gst_plugins') for filename in plugin_path.glob(lib_pattern)
                         if include_or_exclude_file(filename, include_list, exclude_list)]

    hook_api.add_datas(datas)
    hook_api.add_binaries(binaries)
    hook_api.add_imports(*hiddenimports)
