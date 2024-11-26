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
This modest package contains various common humanization utilities, like turning a number into a fuzzy human
readable duration ("3 minutes ago") or into a human readable size or throughput.

https://pypi.org/project/humanize

This hook was tested against humanize 3.5.0.
"""

from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('humanize')
