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
# Hook for the uvloop package: https://pypi.python.org/pypi/uvloop
#
# Tested with uvloop 0.8.1 and Python 3.6.2, on Ubuntu 16.04.1 64bit.

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('uvloop')
