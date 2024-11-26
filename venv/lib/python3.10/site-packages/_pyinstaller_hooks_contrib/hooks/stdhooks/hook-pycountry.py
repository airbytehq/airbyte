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

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# pycountry requires the ISO databases for country data.
# Tested v1.15 on Linux/Ubuntu.
# https://pypi.python.org/pypi/pycountry
datas = copy_metadata('pycountry') + collect_data_files('pycountry')
