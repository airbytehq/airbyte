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

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = (collect_submodules('docutils.languages') +
                 collect_submodules('docutils.writers') +
                 collect_submodules('docutils.parsers.rst.languages') +
                 collect_submodules('docutils.parsers.rst.directives'))
datas = collect_data_files('docutils')
