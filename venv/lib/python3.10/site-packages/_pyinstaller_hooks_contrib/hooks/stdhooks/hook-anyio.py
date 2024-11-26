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
AnyIO contains a number of back-ends as dynamically imported modules.
This hook was tested against AnyIO v1.4.0.
"""

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('anyio._backends')
