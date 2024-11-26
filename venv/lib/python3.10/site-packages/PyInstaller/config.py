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
"""
This module holds run-time PyInstaller configuration.

Variable CONF is a dict() with all configuration options that are necessary for the build phase. Build phase is done by
passing .spec file to exec() function. CONF variable is the only way how to pass arguments to exec() and how to avoid
using 'global' variables.

NOTE: Having 'global' variables does not play well with the test suite because it does not provide isolated environments
for tests. Some tests might fail in this case.

NOTE: The 'CONF' dict() is cleaned after building phase to not interfere with any other possible test.

To pass any arguments to build phase, just do:

    from PyInstaller.config import CONF
    CONF['my_var_name'] = my_value

And to use this variable in the build phase:

    from PyInstaller.config import CONF
    foo = CONF['my_var_name']


This is the list of known variables. (Please update it if necessary.)

cachedir
hiddenimports
noconfirm
pathex
ui_admin
ui_access
upx_available
upx_dir
workpath

tests_modgraph  - cached PyiModuleGraph object to speed up tests

code_cache - dictionary associating `Analysis.pure` list instances with code cache dictionaries. Used by PYZ writer.
"""

# NOTE: Do not import other PyInstaller modules here. Just define constants here.

CONF = {
    # Unit tests require this key to exist.
    'pathex': [],
}
