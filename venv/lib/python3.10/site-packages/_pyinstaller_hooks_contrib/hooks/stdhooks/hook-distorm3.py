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

# Hook for the diStorm3 module: https://pypi.python.org/pypi/distorm3
# Tested with distorm3 3.3.0, Python 2.7, Windows

from PyInstaller.utils.hooks import collect_dynamic_libs

# distorm3 dynamic library should be in the path with other dynamic libraries.
binaries = collect_dynamic_libs('distorm3', destdir='.')
