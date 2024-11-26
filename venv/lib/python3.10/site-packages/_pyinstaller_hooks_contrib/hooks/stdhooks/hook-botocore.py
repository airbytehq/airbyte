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
# Botocore is a low-level interface to a growing number of Amazon Web Services.
# Botocore serves as the foundation for the AWS-CLI command line utilities. It
# will also play an important role in the boto3.x project.
#
# The botocore package is compatible with Python versions 2.6.5, Python 2.7.x,
# and Python 3.3.x and higher.
#
# https://botocore.readthedocs.org/en/latest/
#
# Tested with botocore 1.4.36

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import is_module_satisfies

if is_module_satisfies('botocore >= 1.4.36'):
    hiddenimports = ['html.parser']

datas = collect_data_files('botocore')
