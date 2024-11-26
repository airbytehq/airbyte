# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import eval_statement, collect_submodules

hiddenimports = collect_submodules("ffpyplayer")
binaries = []
# ffpyplayer has an internal variable tells us where the libraries it was using
for bin in eval_statement("import ffpyplayer; print(ffpyplayer.dep_bins)"):
    binaries += [(bin, '.')]
