#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

import sys

from PyInstaller import compat
from PyInstaller.utils.hooks import logger
from PyInstaller.utils.hooks.tcl_tk import collect_tcl_tk_files


def hook(hook_api):
    # Use a hook-function to get the module's attr:`__file__` easily.
    """
    Freeze all external Tcl/Tk data files if this is a supported platform *or* log a non-fatal error otherwise.
    """
    if compat.is_win or compat.is_darwin or compat.is_unix:
        # collect_tcl_tk_files() returns a Tree, so we need to store it into `hook_api.datas` in order to prevent
        # `building.imphook.format_binaries_and_datas` from crashing with "too many values to unpack".
        hook_api.add_datas(collect_tcl_tk_files(hook_api.__file__))
    else:
        logger.error("... skipping Tcl/Tk handling on unsupported platform %s", sys.platform)
