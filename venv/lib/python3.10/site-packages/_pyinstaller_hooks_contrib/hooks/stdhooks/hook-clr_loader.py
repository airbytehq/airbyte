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

from PyInstaller.compat import is_win, is_cygwin
from PyInstaller.utils.hooks import collect_dynamic_libs

# The clr-loader is used by pythonnet 3.x to load CLR (.NET) runtime.
# On Windows, the default runtime is the .NET Framework, and its corresponding
# loader requires DLLs from clr_loader\ffi\dlls to be collected. This runtime
# is supported only on Windows, so we do not have to worry about it on other
# OSes (where Mono or .NET Core are supported).
if is_win or is_cygwin:
    binaries = collect_dynamic_libs("clr_loader")
