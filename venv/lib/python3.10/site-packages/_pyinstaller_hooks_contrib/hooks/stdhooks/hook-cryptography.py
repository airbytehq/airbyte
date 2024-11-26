# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
"""
Hook for cryptography module from the Python Cryptography Authority.
"""

import os.path
import glob

from PyInstaller.compat import EXTENSION_SUFFIXES
from PyInstaller.utils.hooks import collect_submodules, get_module_file_attribute
from PyInstaller.utils.hooks import copy_metadata

# get the package data so we can load the backends
datas = copy_metadata('cryptography')

# Add the backends as hidden imports
hiddenimports = collect_submodules('cryptography.hazmat.backends')

# Add the OpenSSL FFI binding modules as hidden imports
hiddenimports += collect_submodules('cryptography.hazmat.bindings.openssl') + ['_cffi_backend']


# Include the cffi extensions as binaries in a subfolder named like the package.
# The cffi verifier expects to find them inside the package directory for
# the main module. We cannot use hiddenimports because that would add the modules
# outside the package.
binaries = []
cryptography_dir = os.path.dirname(get_module_file_attribute('cryptography'))
for ext in EXTENSION_SUFFIXES:
    ffimods = glob.glob(os.path.join(cryptography_dir, '*_cffi_*%s*' % ext))
    for f in ffimods:
        binaries.append((f, 'cryptography'))
