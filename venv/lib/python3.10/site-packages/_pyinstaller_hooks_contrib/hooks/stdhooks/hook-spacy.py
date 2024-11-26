# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the Apache License 2.0
#
# The full license is available in LICENSE.APL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: Apache-2.0
# ------------------------------------------------------------------
"""
Spacy contains hidden imports and data files which are needed to import it
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("spacy")
hiddenimports = collect_submodules("spacy")
