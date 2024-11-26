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

DIR = os.path.dirname(__file__)
"""
This directory and every sub directory contains tests
"""


def get_test_dirs():

    dirs = []
    # For every directory and sub directory (including cwd)
    for path, _, _ in os.walk(DIR):
        # Add the norm'd path to dirs
        dirs.append(os.path.normpath(path))

    return dirs
