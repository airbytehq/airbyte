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

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Pendulum checks for locale modules via os.path.exists before import.
# If the include_py_files option is turned off, this check fails, pendulum
# will raise a ValueError.
datas = collect_data_files("pendulum.locales", include_py_files=True)
hiddenimports = collect_submodules("pendulum.locales")
