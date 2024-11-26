#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
import sys

# see https://github.com/python/cpython/blob/3.9/Lib/sysconfig.py#L593
# This will exclude `_osx_support`, `distutils`, `distutils.log` for sys.platform != 'darwin'
if sys.platform != 'darwin':
    excludedimports = ["_osx_support"]

# Python 3.6 uses additional modules like `_sysconfigdata_m_linux_x86_64-linux-gnu`, see
# https://github.com/python/cpython/blob/3.6/Lib/sysconfig.py#L417
# Note: Some versions of Anaconda backport this feature to before 3.6. See issue #3105.
# Note: on Windows, python.org and Anaconda python provide _get_sysconfigdata_name, but calling it fails due to sys
# module lacking abiflags attribute. It does work on MSYS2/MINGW python, where we need to collect corresponding file.
try:
    import sysconfig
    hiddenimports = [sysconfig._get_sysconfigdata_name()]
except AttributeError:
    # Either sysconfig has no attribute _get_sysconfigdata_name (i.e., the function does not exist), or this is Windows
    # and the _get_sysconfigdata_name() call failed due to missing sys.abiflags attribute.
    pass
