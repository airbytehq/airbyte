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

from PyInstaller.utils.hooks import collect_submodules

# This seems to be required in python <= 3.9; in later versions, the `dataclasses` module ends up included via a
# different import chain. But for the sake of consistency, keep the hiddenimport for all python versions.
hiddenimports = ['dataclasses']

# Collect submodules of `sspilib.raw` - most of which are cythonized extensions.
hiddenimports += collect_submodules('sspilib.raw')
