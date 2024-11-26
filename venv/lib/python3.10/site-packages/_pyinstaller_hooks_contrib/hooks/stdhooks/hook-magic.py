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

# hook for https://pypi.org/project/python-magic-bin

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = collect_data_files('magic')
binaries = collect_dynamic_libs('magic')
