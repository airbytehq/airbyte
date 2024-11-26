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

# pycparser needs two modules -- lextab.py and yacctab.py -- which it
# generates at runtime if they cannot be imported.
#
# Those modules are written to the current working directory for which
# the running process may not have write permissions, leading to a runtime
# exception.
#
# This hook tells pyinstaller about those hidden imports, avoiding the
# possibility of such runtime failures.

hiddenimports = ['pycparser.lextab', 'pycparser.yacctab']
