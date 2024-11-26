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

# Certifi is a carefully curated collection of Root Certificates for
# validating the trustworthiness of SSL certificates while verifying
# the identity of TLS hosts.

# It has been extracted from the Requests project.

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('certifi')
