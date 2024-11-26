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

# Module scipy.io._ufunc on some other C/C++ extensions. The hidden import is necessary for SciPy 0.13+.
# Thanks to dyadkin; see issue #826.
hiddenimports = ['scipy.special._ufuncs_cxx']
