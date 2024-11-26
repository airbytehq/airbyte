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

from PyInstaller.utils.hooks import check_requirement

hiddenimports = []

# From Python 3.6 and later ``distutils.sysconfig`` takes on the same behaviour as regular ``sysconfig`` of moving the
# config vars to a module (see hook-sysconfig.py). It doesn't use a nice `get module name` function like ``sysconfig``
# does to help us locate it but the module is the same file that ``sysconfig`` uses so we can use the
# ``_get_sysconfigdata_name()`` from regular ``sysconfig``.
try:
    import sysconfig
    hiddenimports += [sysconfig._get_sysconfigdata_name()]
except AttributeError:
    # Either sysconfig has no attribute _get_sysconfigdata_name (i.e., the function does not exist), or this is Windows
    # and the _get_sysconfigdata_name() call failed due to missing sys.abiflags attribute.
    pass

# Starting with setuptools 60.0, the vendored distutils overrides the stdlib one (which will be removed in python 3.12
# anyway), so check if we are using that version. While the distutils override behavior can be controleld via the
# ``SETUPTOOLS_USE_DISTUTILS`` environment variable, the latter may have a different value during the build and at the
# runtime, and so we need to ensure that both stdlib and setuptools variant of distutils are collected.
if check_requirement("setuptools >= 60.0"):
    hiddenimports += ['setuptools._distutils']
