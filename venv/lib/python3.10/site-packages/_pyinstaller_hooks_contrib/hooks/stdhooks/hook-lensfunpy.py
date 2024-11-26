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

from PyInstaller.utils.hooks import collect_data_files
# bundle xml DB files, skip other files (like DLL files on Windows)
datas = list(filter(lambda p: p[0].endswith('.xml'), collect_data_files('lensfunpy')))
hiddenimports = ['numpy', 'enum']
