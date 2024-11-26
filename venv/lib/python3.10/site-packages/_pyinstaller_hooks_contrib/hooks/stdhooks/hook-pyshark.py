# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

# Python wrapper for pyshark(https://pypi.org/project/pyshark/)
# Tested with version 0.4.5

from PyInstaller.utils.hooks import collect_data_files, is_module_satisfies

hiddenimports = ['pyshark.config']

if is_module_satisfies("pyshark < 0.6"):
    hiddenimports += ['py._path.local', 'py._vendored_packages.iniconfig']
    if is_module_satisfies("pyshark >= 0.5"):
        hiddenimports += ["py._io.terminalwriter", "py._builtin"]

datas = collect_data_files('pyshark')
