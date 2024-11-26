# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the Apache License 2.0
#
# The full license is available in LICENSE.APL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: Apache-2.0
# ------------------------------------------------------------------
"""
Office365-REST-Python-Client contains xml templates that are needed by some methods
This hook ensures that all of the data used by the package is bundled
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("office365")
