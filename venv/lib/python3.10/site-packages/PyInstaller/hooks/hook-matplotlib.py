#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller import isolated
from PyInstaller import compat
from PyInstaller.utils import hooks as hookutils


@isolated.decorate
def mpl_data_dir():
    import matplotlib
    return matplotlib.get_data_path()


datas = [
    (mpl_data_dir(), "matplotlib/mpl-data"),
]

binaries = []

# Windows PyPI wheels for `matplotlib` >= 3.7.0 use `delvewheel`.
# In addition to DLLs from `matplotlib.libs` directory, which should be picked up automatically by dependency analysis
# in contemporary PyInstaller versions, we also need to collect the load-order file. This used to be required for
# python <= 3.7 (that lacked `os.add_dll_directory`), but is also needed for Anaconda python 3.8 and 3.9, where
# `delvewheel` falls back to load-order file codepath due to Anaconda breaking `os.add_dll_directory` implementation.
if compat.is_win and hookutils.check_requirement('matplotlib >= 3.7.0'):
    delvewheel_datas, delvewheel_binaries = hookutils.collect_delvewheel_libs_directory('matplotlib')

    datas += delvewheel_datas
    binaries += delvewheel_binaries
