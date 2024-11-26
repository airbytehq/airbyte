#-----------------------------------------------------------------------------
# Copyright (c) 2019-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
`importlib_resources` is a backport of the 3.9+ module `importlib.resources`
"""

from PyInstaller.utils.hooks import check_requirement, collect_data_files

# Prior to v1.2.0, a `version.txt` file is used to set __version__. Later versions use `importlib.metadata`.
if check_requirement("importlib_resources < 1.2.0"):
    datas = collect_data_files("importlib_resources", includes=["version.txt"])

if check_requirement("importlib_resources >= 1.3.1"):
    hiddenimports = ['importlib_resources.trees']
