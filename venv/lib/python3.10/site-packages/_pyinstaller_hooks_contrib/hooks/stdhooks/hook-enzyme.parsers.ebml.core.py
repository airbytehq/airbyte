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
enzyme:
https://github.com/Diaoul/enzyme
"""

import os
from PyInstaller.utils.hooks import get_package_paths

# get path of enzyme
ep = get_package_paths('enzyme')

# add the data
data = os.path.join(ep[1], 'parsers', 'ebml', 'specs', 'matroska.xml')
datas = [(data, "enzyme/parsers/ebml/specs")]
