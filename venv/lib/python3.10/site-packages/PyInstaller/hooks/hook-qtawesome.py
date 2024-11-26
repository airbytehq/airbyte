#-----------------------------------------------------------------------------
# Copyright (c) 2017-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
Hook for QtAwesome (https://github.com/spyder-ide/qtawesome).
Font files and charmaps need to be included with module.
Tested with QtAwesome 0.4.4 and Python 3.6 on macOS 10.12.4.
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('qtawesome')
