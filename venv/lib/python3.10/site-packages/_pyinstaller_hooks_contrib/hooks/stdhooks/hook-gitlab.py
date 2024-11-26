# ------------------------------------------------------------------
# Copyright (c) 2022 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
#
# python-gitlab is a Python package providing access to the GitLab server API.
# It supports the v4 API of GitLab, and provides a CLI tool (gitlab).
#
# https://python-gitlab.readthedocs.io
#
# Tested with gitlab 3.2.0

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('gitlab')
