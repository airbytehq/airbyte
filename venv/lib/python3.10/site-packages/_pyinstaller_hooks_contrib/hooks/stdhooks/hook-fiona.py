# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_data_files, is_module_satisfies

hiddenimports = [
    "fiona._shim",
    "fiona.schema",
    "json",
]

# As of fiona 1.9.0, `fiona.enums` is also a hidden import, made in cythonized `fiona.crs`.
if is_module_satisfies("fiona >= 1.9.0"):
    hiddenimports.append("fiona.enums")

# Collect data files that are part of the package (e.g., projections database)
datas = collect_data_files("fiona")
