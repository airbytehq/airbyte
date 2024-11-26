#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
The matplotlib.numerix package sneaks these imports in under the radar.
"""

hiddenimports = [
    'fft',
    'linear_algebra',
    'random_array',
    'ma',
    'mlab',
]
