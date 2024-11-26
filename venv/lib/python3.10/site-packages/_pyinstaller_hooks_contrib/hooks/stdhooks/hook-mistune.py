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

# Hook for nanite: https://pypi.python.org/pypi/nanite

from PyInstaller.utils.hooks import is_module_satisfies, collect_submodules

# As of version 3.0.0, mistune loads its plugins indirectly (but does so during package import nevertheless).
if is_module_satisfies("mistune >= 3.0.0"):
    hiddenimports = collect_submodules("mistune.plugins")
