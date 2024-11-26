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

from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.hooks import collect_data_files

# googleapiclient.model queries the library version via
# pkg_resources.get_distribution("google-api-python-client").version,
# so we need to collect that package's metadata
datas = copy_metadata('google_api_python_client')
datas += collect_data_files('googleapiclient.discovery_cache', excludes=['*.txt', '**/__pycache__'])
