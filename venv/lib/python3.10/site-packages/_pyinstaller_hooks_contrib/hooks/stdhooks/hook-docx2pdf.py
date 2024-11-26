# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later.
# ------------------------------------------------------------------

# Hook for docx2pdf: https://pypi.org/project/docx2pdf/

from PyInstaller.utils.hooks import copy_metadata, collect_data_files

datas = copy_metadata('docx2pdf')
datas += collect_data_files('docx2pdf')
