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
"""
Module hook for the `scipy.special._ellip_harm_2` C extension first introduced by SciPy >= 0.15.0.

See Also
----------
https://github.com/scipy/scipy/blob/master/scipy/special/_ellip_harm_2.pyx
    This C extension's Cython-based implementation.
"""

# In SciPy >= 0.15.0:
#
# 1. The "scipy.special.__init__" module imports...
# 2. The "scipy.special._ellip_harm" module imports...
# 3. The "scipy.special._ellip_harm_2" C extension imports...
# 4. The "scipy.integrate" package.
#
# The third import is undetectable by PyInstaller and hence explicitly listed. Since "_ellip_harm" and "_ellip_harm_2"
# were first introduced by SciPy 0.15.0, the following hidden import will only be applied for versions of SciPy
# guaranteed to provide these modules and C extensions.
hiddenimports = ['scipy.integrate']
