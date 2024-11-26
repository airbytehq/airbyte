# ------------------------------------------------------------------
# Copyright (c) 2022 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

# Hook for hdf5plugin: https://pypi.org/project/hdf5plugin/

from PyInstaller.utils.hooks import collect_dynamic_libs

datas = collect_dynamic_libs("hdf5plugin")
