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

# When PyQt5.Qt is imported it implies the import of all PyQt5 modules. See
# http://pyqt.sourceforge.net/Docs/PyQt5/Qt.html.
import os

from PyInstaller.utils.hooks import get_module_file_attribute

# Only do this if PyQt5 is found.
mfi = get_module_file_attribute('PyQt5')
if mfi:
    # Determine the name of all these modules by looking in the PyQt5 directory.
    hiddenimports = []
    for f in os.listdir(os.path.dirname(mfi)):
        root, ext = os.path.splitext(os.path.basename(f))
        if root.startswith('Qt') and root != 'Qt':
            # On Linux and OS X, PyQt 5.14.1 has a ``.abi3`` suffix on all library names. Remove it.
            if root.endswith('.abi3'):
                root = root[:-5]
            hiddenimports.append('PyQt5.' + root)
