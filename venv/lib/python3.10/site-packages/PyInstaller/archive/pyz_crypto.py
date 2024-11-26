#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------


class PyiBlockCipher:
    def __init__(self, key=None):
        from PyInstaller.exceptions import RemovedCipherFeatureError
        raise RemovedCipherFeatureError("Please remove cipher and block_cipher parameters from your spec file.")
