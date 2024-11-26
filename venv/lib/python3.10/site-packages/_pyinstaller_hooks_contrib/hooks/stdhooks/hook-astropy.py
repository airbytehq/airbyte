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

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, \
    copy_metadata, is_module_satisfies

# Astropy includes a number of non-Python files that need to be present
# at runtime, so we include these explicitly here.
datas = collect_data_files('astropy')

# In a number of places, astropy imports other sub-modules in a way that is not
# always auto-discovered by pyinstaller, so we always include all submodules.
hiddenimports = collect_submodules('astropy')

# We now need to include the *_parsetab.py and *_lextab.py files for unit and
# coordinate parsing, since these are loaded as files rather than imported as
# sub-modules. We leverage collect_data_files to get all files in astropy then
# filter these.
ply_files = []
for path, target in collect_data_files('astropy', include_py_files=True):
    if path.endswith(('_parsetab.py', '_lextab.py')):
        ply_files.append((path, target))

datas += ply_files

# Astropy version >= 5.0 queries metadata to get version information.
if is_module_satisfies('astropy >= 5.0'):
    datas += copy_metadata('astropy')
    datas += copy_metadata('numpy')

# In the Cython code, Astropy imports numpy.lib.recfunctions which isn't
# automatically discovered by pyinstaller, so we add this as a hidden import.
hiddenimports += ['numpy.lib.recfunctions']
