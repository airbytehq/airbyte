# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

# Tested with IPython 4.0.0.

from PyInstaller.compat import is_win, is_darwin
from PyInstaller.utils.hooks import collect_data_files

# Ignore 'matplotlib'. IPython contains support for matplotlib.
# Ignore GUI libraries. IPython supports integration with GUI frameworks.
# Assume that it will be imported by any other module when the user really
# uses it.
excludedimports = ['gtk', 'matplotlib', 'PyQt4', 'PyQt5', 'PySide']

# IPython uses 'tkinter' for clipboard access on Linux/Unix. Exclude it on Windows and OS X.
if is_win or is_darwin:
    excludedimports.append('tkinter')

datas = collect_data_files('IPython')

# IPython imports extensions by changing to the extensions directory and using
# importlib.import_module, so we need to copy over the extensions as if they
# were data files.
datas += collect_data_files('IPython.extensions', include_py_files=True)
