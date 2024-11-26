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

from PyInstaller.utils.hooks import collect_submodules

# Tested on Windows 7 x64 with Python 2.7.6 x32 using ReportLab 3.0
# This has been observed to *not* work on ReportLab 2.7
hiddenimports = collect_submodules('reportlab.pdfbase',
                                   lambda name: name.startswith('reportlab.pdfbase._fontdata_'))
