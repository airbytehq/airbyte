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

# Handlers are imported by a lazy-load proxy, based on a
# name-to-package mapping. Collect all handlers to ease packaging.
# If you want to reduce the size of your application, used
# `--exclude-module` to remove unused ones.
hiddenimports = [
    "passlib.handlers",
    "passlib.handlers.digests",
    "configparser",
]
