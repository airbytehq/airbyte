# ------------------------------------------------------------------
# Copyright (c) 2022 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_submodules, copy_metadata, collect_data_files

# Collect submodules to ensure that checker plugins are collected. but avoid collecting tests sub-package.
hiddenimports = collect_submodules('compliance_checker', filter=lambda name: name != 'compliance_checker.tests')

# Copy metadata, because checker plugins are discovered via entry-points
datas = copy_metadata('compliance_checker')

# Include data files from compliance_checker/data sub-directory.
datas += collect_data_files('compliance_checker', includes=['data/**'])
