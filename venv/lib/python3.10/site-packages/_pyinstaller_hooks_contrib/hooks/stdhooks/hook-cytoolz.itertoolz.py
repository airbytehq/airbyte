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

# Hook for the cytoolz package: https://pypi.python.org/pypi/cytoolz
# Tested with cytoolz 0.9.0 and Python 3.5.2, on Ubuntu Linux x64

hiddenimports = ['cytoolz.utils', 'cytoolz._signatures']
