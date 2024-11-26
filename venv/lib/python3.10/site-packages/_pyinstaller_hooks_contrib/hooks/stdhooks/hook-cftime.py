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

# The cftime._cftime is a cython exension with following hidden imports:
hiddenimports = [
    're',
    'time',
    'datetime',
    'warnings',
    'numpy',
    'cftime._strptime',
]
