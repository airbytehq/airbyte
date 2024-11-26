#-----------------------------------------------------------------------------
# Copyright (c) 2014-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.utils.hooks.qt import \
    add_qt5_dependencies, pyqt5_library_info

# Ensure PyQt5 is importable before adding info depending on it.
if pyqt5_library_info.version is not None:
    hiddenimports, binaries, datas = add_qt5_dependencies(__file__)

    # Include helper process executable, translations, and resources.
    webengine_binaries, webengine_datas = pyqt5_library_info.collect_qtwebengine_files()
    binaries += webengine_binaries
    datas += webengine_datas
