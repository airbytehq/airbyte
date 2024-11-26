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
"""
Hook for flirpy, a library to interact with FLIR thermal imaging cameras and images.
https://github.com/LJMUAstroEcology/flirpy
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('flirpy')
