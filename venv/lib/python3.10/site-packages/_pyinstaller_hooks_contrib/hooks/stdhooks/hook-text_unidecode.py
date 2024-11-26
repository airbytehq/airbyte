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
# -----------------------------------------------------------------------------
"""
text-unidecode:
https://github.com/kmike/text-unidecode/
"""

import os
from PyInstaller.utils.hooks import get_package_paths

package_path = get_package_paths("text_unidecode")
data_bin_path = os.path.join(package_path[1], "data.bin")

if os.path.exists(data_bin_path):
    datas = [(data_bin_path, 'text_unidecode')]
