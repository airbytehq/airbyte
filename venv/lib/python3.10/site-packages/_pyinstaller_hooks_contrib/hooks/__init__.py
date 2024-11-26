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
import os


def get_hook_dirs():
    hooks_dir = os.path.dirname(__file__)
    return [
        # Required because standard hooks are in sub-directory instead of the top-level hooks directory.
        os.path.join(hooks_dir, 'stdhooks'),
        # pre_* and run-time hooks
        hooks_dir,
    ]
