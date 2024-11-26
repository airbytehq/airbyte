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

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

# Collect dynamic extensions from torchtext/lib - some of them are loaded dynamically, and are thus not automatically
# collected.
binaries = collect_dynamic_libs('torchtext')
hiddenimports = collect_submodules('torchtext.lib')

# Collect source .py files for JIT/torchscript. Requires PyInstaller >= 5.3, no-op in older versions.
module_collection_mode = 'pyz+py'
