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

from PyInstaller.compat import is_darwin, is_win

modules = ["platformdirs"]

# platfromdirs contains dynamically loaded per-platform submodules.
if is_darwin:
    modules.append("platformdirs.macos")
elif is_win:
    modules.append("platformdirs.windows")
else:
    # default to unix for all other platforms
    # this includes unix, cygwin, and msys2
    modules.append("platformdirs.unix")

hiddenimports = modules
