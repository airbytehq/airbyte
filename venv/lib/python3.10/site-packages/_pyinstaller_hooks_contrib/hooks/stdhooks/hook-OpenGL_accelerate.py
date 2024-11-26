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
OpenGL_accelerate contais modules written in cython. This module
should speed up some functions from OpenGL module. The following
hiddenimports are not resolved by PyInstaller because OpenGL_accelerate
is compiled to native Python modules.
"""

hiddenimports = [
    'OpenGL_accelerate.wrapper',
    'OpenGL_accelerate.formathandler',
]
