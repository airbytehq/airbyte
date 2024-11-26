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

from PyInstaller.utils.hooks import collect_data_files

# We need to include modules in PyQt5.uic.widget-plugins, so they can be dynamically loaded by uic. They should be
# included as separate (data-like) files, so they can be found by os.listdir and friends. However, as this directory
# is not a package, refer to it using the package (PyQt5.uic) followed by the subdirectory name (``widget-plugins/``).
datas = collect_data_files('PyQt5.uic', True, 'widget-plugins')
