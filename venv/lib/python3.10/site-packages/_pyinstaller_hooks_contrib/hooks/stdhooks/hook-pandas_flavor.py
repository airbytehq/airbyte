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

# As of version 0.3.0, pandas_flavor uses lazy loader to import `register` and `xarray` sub-modules. In earlier
# versions, these used to be imported directly.
hiddenimports = ['pandas_flavor.register', 'pandas_flavor.xarray']
