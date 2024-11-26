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
#
# NumPy aware dynamic Python compiler using LLVM
# https://github.com/numba/numba
#
# Tested with:
# numba 0.26 (Anaconda 4.1.1, Windows), numba 0.28 (Linux)

excludedimports = ["IPython", "scipy"]
hiddenimports = ["llvmlite"]
