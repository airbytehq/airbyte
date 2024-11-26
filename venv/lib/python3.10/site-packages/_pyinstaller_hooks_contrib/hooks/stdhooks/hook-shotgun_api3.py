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

from PyInstaller.utils.hooks import collect_data_files

# Shotgun is using "six" to import these and
# PyInstaller does not seem to catch them correctly.
hiddenimports = ["xmlrpc", "xmlrpc.client"]

# Collect the following files:
#   /shotgun_api3/lib/httplib2/python2/cacerts.txt
#   /shotgun_api3/lib/httplib2/python3/cacerts.txt
#   /shotgun_api3/lib/certifi/cacert.pem
datas = collect_data_files("shotgun_api3")
