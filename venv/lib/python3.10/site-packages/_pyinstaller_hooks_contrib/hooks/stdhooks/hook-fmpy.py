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
"""
Hook for FMPy, a library to simulate Functional Mockup Units (FMUs)
https://github.com/CATIA-Systems/FMPy

Adds the data files that are required at runtime:

- XSD schema files
- dynamic libraries for the CVode solver
- source and header files for the compilation of c-code FMUs
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('fmpy')
