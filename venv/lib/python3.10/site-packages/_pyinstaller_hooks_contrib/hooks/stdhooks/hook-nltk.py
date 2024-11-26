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

# hook for nltk
import nltk
import os
from PyInstaller.utils.hooks import collect_data_files

# add datas for nltk
datas = collect_data_files('nltk', False)

# loop through the data directories and add them
for p in nltk.data.path:
    if os.path.exists(p):
        datas.append((p, "nltk_data"))

# nltk.chunk.named_entity should be included
hiddenimports = ["nltk.chunk.named_entity"]
