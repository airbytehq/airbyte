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

from PyInstaller.utils.hooks import get_module_file_attribute

# Compiler (see class BaseDatabaseOperations)
hiddenimports = ['django.db.models.sql.compiler']

# Include all available Django backends.
modpath = os.path.dirname(get_module_file_attribute('django.db.backends'))
for fn in glob.glob(os.path.join(modpath, '*')):
    if os.path.isdir(fn):
        fn = os.path.basename(fn)
        hiddenimports.append('django.db.backends.' + fn + '.base')
