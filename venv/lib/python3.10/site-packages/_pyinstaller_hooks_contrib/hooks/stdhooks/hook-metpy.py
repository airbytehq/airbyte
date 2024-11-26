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

from PyInstaller.utils.hooks import copy_metadata, collect_data_files

# MetPy requires metadata, because it queries its version via
# pkg_resources.get_distribution(__package__).version or, in newer
# versions, importlib.metadata.version(__package__)
datas = copy_metadata('metpy')

# Collect data files
datas += collect_data_files('metpy')
