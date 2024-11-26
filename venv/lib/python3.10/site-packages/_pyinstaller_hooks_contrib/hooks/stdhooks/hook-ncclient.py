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
"""
Hook for ncclient. ncclient is a Python library that facilitates client-side
scripting and application development around the NETCONF protocol.
https://pypi.python.org/pypi/ncclient

This hook was tested with ncclient 0.4.3.
"""
from PyInstaller.utils.hooks import collect_submodules

# Modules 'ncclient.devices.*' are dynamically loaded and PyInstaller
# is not able to find them.
hiddenimports = collect_submodules('ncclient.devices')
