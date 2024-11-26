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
# hook for https://github.com/hbldh/bleak

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
from PyInstaller.compat import is_win

if is_win:
    datas = collect_data_files('bleak', subdir=r'backends\dotnet')
    binaries = collect_dynamic_libs('bleak')
