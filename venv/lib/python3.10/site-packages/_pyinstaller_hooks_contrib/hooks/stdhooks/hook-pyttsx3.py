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

# pyttsx3 conditionally imports drivers module based on specific platform.
# https://github.com/nateshmbhat/pyttsx3/blob/5a19376a94fdef6bfaef8795539e755b1f363fbf/pyttsx3/driver.py#L40-L50

import sys

hiddenimports = ["pyttsx3.drivers", "pyttsx3.drivers.dummy"]

# Take directly from the link above.
if sys.platform == 'darwin':
    driverName = 'nsss'
elif sys.platform == 'win32':
    driverName = 'sapi5'
else:
    driverName = 'espeak'
# import driver module
name = 'pyttsx3.drivers.%s' % driverName

hiddenimports.append(name)
