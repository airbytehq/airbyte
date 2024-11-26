# ------------------------------------------------------------------
# Copyright (c) 2023 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import logger, is_module_satisfies

# With sympy 1.12, PyInstaller's modulegraph analysis hits the recursion limit.
# So, unless the user has already done so, increase it automatically.
if is_module_satisfies('sympy >= 1.12'):
    import sys
    new_limit = 5000
    if sys.getrecursionlimit() < new_limit:
        logger.info("hook-sympy: raising recursion limit to %d", new_limit)
        sys.setrecursionlimit(new_limit)
