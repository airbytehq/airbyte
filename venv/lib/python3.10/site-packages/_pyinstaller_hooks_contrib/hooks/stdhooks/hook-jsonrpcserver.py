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

# This is needed to bundle request-schema.json file needed by
# jsonrpcserver package

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('jsonrpcserver')
