# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import is_module_satisfies, collect_submodules

# The MariaDB uses a .pyd file that imports ``decimal`` module within its
# module initialization function. On recent python versions (> 3.8), the decimal
# module seems to be picked up nevertheless (presumably due to import in some
# other module), but it is better not to rely on that, and ensure it is always
# collected as a hidden import.
hiddenimports = ['decimal']

# mariadb >= 1.1.0 requires several hidden imports from mariadb.constants.
# Collect them all, just to be on the safe side...
if is_module_satisfies("mariadb >= 1.1.0"):
    hiddenimports += collect_submodules("mariadb.constants")
