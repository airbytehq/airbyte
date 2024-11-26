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
#
# Boto3, the next version of Boto, is now stable and recommended for general
# use.
#
# Boto is an integrated interface to current and future infrastructural
# services offered by Amazon Web Services.
#
# http://boto.readthedocs.org/en/latest/
#
# Tested with boto 2.38.0

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('boto')
