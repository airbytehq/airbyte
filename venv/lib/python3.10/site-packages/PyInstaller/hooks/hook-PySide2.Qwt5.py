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

hiddenimports = ['PySide2.QtCore', 'PySide2.QtWidgets', 'PySide2.QtGui', 'PySide2.QtSvg']


@isolated.decorate
def conditional_imports():
    from PySide2 import Qwt5

    out = []
    if hasattr(Qwt5, "toNumpy"):
        out.append("numpy")
    if hasattr(Qwt5, "toNumeric"):
        out.append("numeric")
    if hasattr(Qwt5, "toNumarray"):
        out.append("numarray")
    return out


hiddenimports += conditional_imports()
