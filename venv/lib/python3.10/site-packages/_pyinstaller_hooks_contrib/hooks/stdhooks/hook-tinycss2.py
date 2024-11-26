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
Hook for tinycss2. tinycss2 is a low-level CSS parser and generator.
https://github.com/Kozea/tinycss2
"""
from PyInstaller.utils.hooks import collect_data_files


# Hook no longer required for tinycss2 >= 1.0.0
def hook(hook_api):
    hook_api.add_datas(collect_data_files(hook_api.__name__))
