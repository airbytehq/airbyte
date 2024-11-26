# ------------------------------------------------------------------
# Copyright (c) 2022 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

# Forced import of these modules happens on first orjson import
# and orjson is a compiled extension module.
hiddenimports = [
    'uuid',
    'zoneinfo',
    'enum',
    'json',
    'dataclasses',
]
