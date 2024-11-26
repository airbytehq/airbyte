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

hiddenimports = [
    # win32com client and server util
    # modules could be hidden imports
    # of some modules using win32com.
    # Included for completeness.
    'win32com.client.util',
    'win32com.server.util',
]
