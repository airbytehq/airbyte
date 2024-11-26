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
APScheduler uses entry points to dynamically load executors, job
stores and triggers.
This hook was tested against APScheduler 3.6.3.
"""

from PyInstaller.utils.hooks import (collect_submodules, copy_metadata,
                                     is_module_satisfies)

if is_module_satisfies("apscheduler < 4"):
    if is_module_satisfies("pyinstaller >= 4.4"):
        datas = copy_metadata('APScheduler', recursive=True)
    else:
        datas = copy_metadata('APScheduler')

    hiddenimports = collect_submodules('apscheduler')
