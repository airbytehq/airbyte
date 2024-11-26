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

# Hook for https://github.com/PyWavelets/pywt

hiddenimports = ['pywt._extensions._cwt']

# NOTE: There is another project `https://github.com/Knapstad/pywt installing
# a packagre `pywt`, too. This name clash is not much of a problem, even if
# this hook is picked up for the other package, since PyInstaller will simply
# skip any module added by this hook but acutally missing. If the other project
# requires a hook, too, simply add it to this file.
