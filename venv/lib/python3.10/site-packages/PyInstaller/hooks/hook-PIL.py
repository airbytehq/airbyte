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

# This hook was tested with Pillow 2.9.0 (Maintained fork of PIL):
# https://pypi.python.org/pypi/Pillow

# Ignore tkinter to prevent inclusion of Tcl/Tk library and other GUI libraries. Assume that if people are really using
# tkinter in their application, they will also import it directly and thus PyInstaller bundles the right GUI library.
excludedimports = ['tkinter', 'PyQt5', 'PySide2', 'PyQt6', 'PySide6']

# Similarly, prevent inclusion of IPython, which in turn ends up pulling in whole matplotlib, along with its optional
# GUI library dependencies.
excludedimports += ['IPython']
