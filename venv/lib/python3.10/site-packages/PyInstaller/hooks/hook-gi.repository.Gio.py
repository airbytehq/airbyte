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

from PyInstaller import compat
import PyInstaller.log as logging
from PyInstaller.utils.hooks.gi import GiModuleInfo

logger = logging.getLogger(__name__)

module_info = GiModuleInfo('Gio', '2.0')
if module_info.available:
    binaries, datas, hiddenimports = module_info.collect_typelib_data()

    # Find Gio modules
    libdir = module_info.get_libdir()
    modules_pattern = None

    if compat.is_win:
        modules_pattern = os.path.join(libdir, 'gio', 'modules', '*.dll')
    else:
        gio_libdir = os.path.join(libdir, 'gio', 'modules')
        if not os.path.exists(gio_libdir):
            # homebrew installs the files elsewhere...
            gio_libdir = os.path.join(os.path.commonprefix([compat.base_prefix, gio_libdir]), 'lib', 'gio', 'modules')

        if os.path.exists(gio_libdir):
            modules_pattern = os.path.join(gio_libdir, '*.so')
        else:
            logger.warning('Could not determine Gio modules path!')

    if modules_pattern:
        for f in glob.glob(modules_pattern):
            binaries.append((f, 'gio_modules'))
    else:
        # To add a new platform add a new elif above with the proper is_<platform> and proper pattern for finding the
        # Gio modules on your platform.
        logger.warning('Bundling Gio modules is not supported on your platform.')

    # Bundle the mime cache -- might not be needed on Windows
    # -> this is used for content type detection (also used by GdkPixbuf)
    # -> gio/xdgmime/xdgmime.c looks for mime/mime.cache in the users home directory, followed by XDG_DATA_DIRS if
    #    specified in the environment, otherwise it searches /usr/local/share/ and /usr/share/
    if not compat.is_win:
        _mime_searchdirs = ['/usr/local/share', '/usr/share']
        if 'XDG_DATA_DIRS' in os.environ:
            _mime_searchdirs.insert(0, os.environ['XDG_DATA_DIRS'])

        for sd in _mime_searchdirs:
            spath = os.path.join(sd, 'mime', 'mime.cache')
            if os.path.exists(spath):
                datas.append((spath, 'share/mime'))
                break
