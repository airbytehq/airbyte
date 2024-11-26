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

# Tested on Windows 7 64bit with python 2.7.6 and PsychoPy 1.81.03

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('psychopy')
