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

# This hook was tested with Pillow 2.9.0 (Maintained fork of PIL): https://pypi.python.org/pypi/Pillow

from PyInstaller.utils.hooks import collect_submodules

# Include all PIL image plugins - module names containing 'ImagePlugin'. e.g.  PIL.JpegImagePlugin
hiddenimports = collect_submodules('PIL', lambda name: 'ImagePlugin' in name)
