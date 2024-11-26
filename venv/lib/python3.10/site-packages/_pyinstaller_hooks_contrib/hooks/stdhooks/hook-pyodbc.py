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

from PyInstaller.utils.hooks import get_pyextension_imports

# It's hard to detect imports of binary Python module without importing it.
# Let's try importing that module in a subprocess.
# TODO function get_pyextension_imports() is experimental and we need
#      to evaluate its usage here and its suitability for other hooks.
hiddenimports = get_pyextension_imports('pyodbc')
