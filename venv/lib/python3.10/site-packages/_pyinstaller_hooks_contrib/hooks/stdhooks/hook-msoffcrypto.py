# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the Apache License 2.0
#
# The full license is available in LICENSE.APL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: Apache-2.0
# ------------------------------------------------------------------
"""
msoffcrypto contains hidden metadata as of v4.12.0
"""

from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('msoffcrypto-tool')
