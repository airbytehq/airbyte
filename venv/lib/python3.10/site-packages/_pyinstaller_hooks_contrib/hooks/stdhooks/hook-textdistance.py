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

# Hook for textdistance: https://pypi.org/project/textdistance/4.1.3/

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('textdistance')
