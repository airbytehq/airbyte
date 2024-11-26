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
# Azurerm is a lite api to microsoft azure.
# Azurerm is using pkg_resources internally which is not supported by py-installer.
# This hook will collect the module metadata.
# Tested with Azurerm 0.10.0

from PyInstaller.utils.hooks import copy_metadata, is_module_satisfies

if is_module_satisfies("pyinstaller >= 4.4"):
    datas = copy_metadata("azurerm", recursive=True)
else:
    datas = copy_metadata("azurerm")
