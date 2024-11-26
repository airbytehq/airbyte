#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

# Hook for https://pypi.org/project/Scrapy/
# https://stackoverflow.com/questions/49085970/no-such-file-or-directory-error-using-pyinstaller-and-scrapy

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('scrapy')
hiddenimports = collect_submodules('scrapy')
