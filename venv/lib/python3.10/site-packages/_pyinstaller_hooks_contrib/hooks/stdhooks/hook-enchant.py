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
Import hook for PyEnchant.

Tested with PyEnchant 1.6.6.
"""

import os

from PyInstaller.compat import is_darwin
from PyInstaller.utils.hooks import exec_statement, collect_data_files, \
    collect_dynamic_libs, get_installer

# TODO Add Linux support
# Collect first all files that were installed directly into pyenchant
# package directory and this includes:
# - Windows: libenchat-1.dll, libenchat_ispell.dll, libenchant_myspell.dll, other
#            dependent dlls and dictionaries for several languages (de, en, fr)
# - Mac OS X: usually libenchant.dylib and several dictionaries when installed via pip.
binaries = collect_dynamic_libs('enchant')
datas = collect_data_files('enchant')
excludedimports = ['enchant.tests']

# On OS X try to find files from Homebrew or Macports environments.
if is_darwin:
    # Note: env. var. ENCHANT_PREFIX_DIR is implemented only in the development version:
    #    https://github.com/AbiWord/enchant
    #    https://github.com/AbiWord/enchant/pull/2
    # TODO Test this hook with development version of enchant.
    libenchant = exec_statement("""
        from enchant._enchant import e
        print(e._name)
    """).strip()

    installer = get_installer('enchant')
    if installer != 'pip':
        # Note: Name of detected enchant library is 'libenchant.dylib'. However, it
        #       is just symlink to 'libenchant.1.dylib'.
        binaries.append((libenchant, '.'))

        # Collect enchant backends from Macports. Using same file structure as on Windows.
        backends = exec_statement("""
            from enchant import Broker
            for provider in Broker().describe():
                print(provider.file)""").strip().split()
        binaries.extend([(b, 'enchant/lib/enchant') for b in backends])

        # Collect all available dictionaries from Macports. Using same file structure as on Windows.
        # In Macports are available mostly hunspell (myspell) and aspell dictionaries.
        libdir = os.path.dirname(libenchant)  # e.g. /opt/local/lib
        sharedir = os.path.join(os.path.dirname(libdir), 'share')  # e.g. /opt/local/share
        if os.path.exists(os.path.join(sharedir, 'enchant')):
            datas.append((os.path.join(sharedir, 'enchant'), 'enchant/share/enchant'))
        if os.path.exists(os.path.join(sharedir, 'enchant-2')):
            datas.append((os.path.join(sharedir, 'enchant-2'), 'enchant/share/enchant-2'))
