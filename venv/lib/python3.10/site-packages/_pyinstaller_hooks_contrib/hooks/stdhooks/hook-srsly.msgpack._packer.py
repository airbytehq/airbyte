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
srsly.msgpack._packer contains hidden imports which are needed to import it
This hook was created to make spacy work correctly.
"""

hiddenimports = ['srsly.msgpack.util']
