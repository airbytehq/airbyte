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

import os

from PyInstaller.utils.hooks import logger, get_module_attribute

# Query the `libpath` attribute of the `gmsh` module to obtain the path to shared library. This way, we do not need to
# duplicate the discovery logic.
try:
    lib_file = get_module_attribute('gmsh', 'libpath')
except Exception:
    logger.warning("Failed to query gmsh.libpath!", exc_info=True)
    lib_file = None

if lib_file and os.path.isfile(lib_file):
    binaries = [(lib_file, '.')]
else:
    logger.warning("Could not find gmsh shared library - gmsh will likely fail to load at run-time!")
