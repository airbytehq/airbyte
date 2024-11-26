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

# This is needed to bundle draft3.json and draft4.json files that come with jsonschema module.
# NOTE: with jsonschema >= 4.18.0, the specification files are part of jsonschema_specifications package, and are
# handled by the corresponding hook-jsonschema.

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = collect_data_files('jsonschema')
datas += copy_metadata('jsonschema')
