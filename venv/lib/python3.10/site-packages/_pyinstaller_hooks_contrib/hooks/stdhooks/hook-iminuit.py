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

# add hooks for iminuit: https://github.com/scikit-hep/iminuit

# iminuit imports subpackages through a cython module which aren't
# found by default

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []

# the iminuit package contains tests which aren't needed when distributing
for mod in collect_submodules('iminuit'):
    if not mod.startswith('iminuit.tests'):
        hiddenimports.append(mod)
