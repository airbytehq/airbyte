# -----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------
"""
This hook does not move a module that can be installed by a package manager, but points to a PyInstaller internal
module that can be imported into the users python instance.

The module is implemented in 'PyInstaller/fake-modules/pyi_splash.py'.
"""

import os

from PyInstaller import PACKAGEPATH
from PyInstaller.utils.hooks import logger


def pre_find_module_path(api):
    try:
        # Test if a module named 'pyi_splash' is locally installed. This prevents that a potentially required dependency
        # is not packed
        import pyi_splash  # noqa: F401
    except ImportError:
        module_dir = os.path.join(PACKAGEPATH, 'fake-modules')

        api.search_dirs = [module_dir]
        logger.info('Adding pyi_splash module to application dependencies.')
    else:
        logger.info('A local module named "pyi_splash" is installed. Use the installed one instead.')
        return
