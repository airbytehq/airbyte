# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
"""
pyttsx imports drivers module based on specific platform.
Found at http://mrmekon.tumblr.com/post/5272210442/pyinstaller-and-pyttsx
"""

hiddenimports = [
    'drivers',
    'drivers.dummy',
    'drivers.espeak',
    'drivers.nsss',
    'drivers.sapi5',
]
