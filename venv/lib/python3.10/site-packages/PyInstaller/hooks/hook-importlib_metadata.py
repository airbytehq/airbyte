#-----------------------------------------------------------------------------
# Copyright (c) 2019-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
importlib_metadata is a library to access the metadata for a Python package. This functionality intends to replace most
uses of pkg_resources entry point API and metadata API.
"""

from PyInstaller.utils.hooks import copy_metadata

# Normally, we should never need to use copy_metadata() in a hook since metadata requirements detection is now
# automatic. However, that detection first uses `PyiModuleGraph.get_code_using("importlib_metadata")` to find
# files which `import importlib_metadata` and `get_code_using()` intentionally excludes internal imports. This
# means that importlib_metadata is not scanned for usages of importlib_metadata and therefore when
# importlib_metadata uses its own API to get its version, this goes undetected. Therefore, we must collect its
# metadata manually.
datas = copy_metadata('importlib_metadata')
