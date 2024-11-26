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

# Hook for appy.pod: https://pypi.python.org/pypi/appy/0.9.1

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('appy.pod', True)
