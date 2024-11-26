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

from PyInstaller.utils.hooks.qt import add_qt6_dependencies

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)

# Using PySide6 true_properties ("from __feature__ import true_properties") causes a hidden dependency on
# QtMultimediaWidgets python module:
# https://github.com/qtproject/pyside-pyside-setup/blob/v6.2.2.1/sources/shiboken6/shibokenmodule/files.dir/shibokensupport/signature/mapping.py#L614-L627
hiddenimports += ['PySide6.QtMultimediaWidgets']
