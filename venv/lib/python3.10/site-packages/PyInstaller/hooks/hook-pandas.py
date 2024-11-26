#-----------------------------------------------------------------------------
# Copyright (c) 2017-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_submodules, check_requirement

# Pandas keeps Python extensions loaded with dynamic imports here.
hiddenimports = collect_submodules('pandas._libs')

# Pandas 1.2.0 and later require cmath hidden import on linux and macOS. On Windows, this is not strictly required, but
# we add it anyway to keep things simple (and future-proof).
if check_requirement('pandas >= 1.2.0'):
    hiddenimports += ['cmath']
