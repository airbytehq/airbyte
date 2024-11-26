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

# Hook for the unidecode package: https://pypi.python.org/pypi/unidecode
# Tested with Unidecode 0.4.21 and Python 3.6.2, on Windows 10 x64.

from PyInstaller.utils.hooks import collect_submodules

# Unidecode dynamically imports modules with relevant character mappings.
# Non-ASCII characters are ignored if the mapping files are not found.
hiddenimports = collect_submodules('unidecode')
