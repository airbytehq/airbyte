#-----------------------------------------------------------------------------
# Copyright (c) 2014-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

# Collect backends
hiddenimports = collect_submodules('keyring.backends')

# Keyring performs backend plugin discovery using setuptools entry points, which are listed in the metadata. Therefore,
# we need to copy the metadata, otherwise no backends will be found at run-time.
datas = copy_metadata('keyring')
