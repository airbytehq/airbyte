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
    add_qt6_dependencies, pyside6_library_info

# Ensure PySide6 is importable before adding info depending on it.
if pyside6_library_info.version is not None:
    # Qt6 prior to 6.2.2 contains a bug that makes it incompatible with the way PyInstaller collects
    # QtWebEngine shared libraries and resources. So exit here and now instead of producing a defunct build.
    if pyside6_library_info.version < [6, 2, 2]:
        raise SystemExit("Error: PyInstaller's QtWebEngine support requires Qt6 6.2.2 or later!")

    hiddenimports, binaries, datas = add_qt6_dependencies(__file__)

    # Include helper process executable, translations, and resources.
    webengine_binaries, webengine_datas = pyside6_library_info.collect_qtwebengine_files()
    binaries += webengine_binaries
    datas += webengine_datas

    hiddenimports += ['PySide6.QtPrintSupport']
