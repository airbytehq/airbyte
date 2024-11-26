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
Hook for Cryptodome module: https://pypi.python.org/pypi/pycryptodomex

Tested with Cryptodomex 3.4.2, Python 2.7 & 3.5, Windows
"""

import os
import glob

from PyInstaller.compat import EXTENSION_SUFFIXES
from PyInstaller.utils.hooks import get_module_file_attribute

# Include the modules as binaries in a subfolder named like the package.
# Cryptodome's loader expects to find them inside the package directory for
# the main module. We cannot use hiddenimports because that would add the
# modules outside the package.

binaries = []
binary_module_names = [
    'Cryptodome.Cipher',
    'Cryptodome.Util',
    'Cryptodome.Hash',
    'Cryptodome.Protocol',
    'Cryptodome.Math',
    'Cryptodome.PublicKey',
]

for module_name in binary_module_names:
    m_dir = os.path.dirname(get_module_file_attribute(module_name))
    for ext in EXTENSION_SUFFIXES:
        module_bin = glob.glob(os.path.join(m_dir, '_*%s' % ext))
        for f in module_bin:
            binaries.append((f, module_name.replace('.', '/')))
