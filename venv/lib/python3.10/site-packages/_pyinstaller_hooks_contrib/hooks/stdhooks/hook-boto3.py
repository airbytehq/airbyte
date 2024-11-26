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
# Boto is the Amazon Web Services (AWS) SDK for Python, which allows Python
# developers to write software that makes use of Amazon services like S3 and
# EC2. Boto provides an easy to use, object-oriented API as well as low-level
# direct service access.
#
# http://boto3.readthedocs.org/en/latest/
#
# Tested with boto3 1.2.1

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = (
    collect_submodules('boto3.dynamodb') +
    collect_submodules('boto3.ec2') +
    collect_submodules('boto3.s3')
)
datas = collect_data_files('boto3')
