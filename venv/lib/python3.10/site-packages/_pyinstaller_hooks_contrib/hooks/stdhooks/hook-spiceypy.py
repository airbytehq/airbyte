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

# Hook for spiceypy: https://pypi.org/project/spiceypy/
# Tested on Ubuntu 20.04 with spiceypy 5.1.1

from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs("spiceypy")
