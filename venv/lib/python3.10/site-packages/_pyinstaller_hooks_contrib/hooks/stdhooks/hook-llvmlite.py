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
# A lightweight LLVM python binding for writing JIT compilers
# https://github.com/numba/llvmlite
#
# Tested with:
# llvmlite 0.11 (Anaconda 4.1.1, Windows), llvmlite 0.13 (Linux)

from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs("llvmlite")
