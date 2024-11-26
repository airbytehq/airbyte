# ------------------------------------------------------------------
# Copyright (c) 2020-2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import is_module_satisfies

hiddenimports = ["decimal"]
# In newer versions of pymssql,  the _mssql was under pymssql
if is_module_satisfies("pymssql > 2.1.5"):
    hiddenimports += ["pymssql._mssql", "uuid"]
else:
    hiddenimports += ["_mssql"]
