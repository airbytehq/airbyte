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
#
# lxml is not fully embedded when using standard hiddenimports
# see https://github.com/pyinstaller/pyinstaller/issues/5306
#
# Tested with lxml 4.6.1

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('lxml')
