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

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

hiddenimports = collect_submodules("sunpy", filter=lambda x: "tests" not in x.split("."))
datas = collect_data_files("sunpy", excludes=['**/tests/', '**/test/'])
datas += collect_data_files("drms")
datas += copy_metadata("sunpy")

# Note : sunpy > 3.1.0 comes with it's own hook for running tests.
