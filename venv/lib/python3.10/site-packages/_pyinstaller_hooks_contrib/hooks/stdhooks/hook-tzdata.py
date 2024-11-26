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

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect timezone data files
datas = collect_data_files("tzdata")

# Collect submodules; each data subdirectory is in fact a package
# (e.g., zoneinfo.Europe), so we need its __init__.py for data files
# (e.g., zoneinfo/Europe/Ljubljana) to be discoverable via
# importlib.resources
hiddenimports = collect_submodules("tzdata")
