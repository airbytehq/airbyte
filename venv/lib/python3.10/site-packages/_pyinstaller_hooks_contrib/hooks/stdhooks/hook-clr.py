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

# There is a name clash between pythonnet's clr module/extension (which this hooks is for) and clr package that provides
# the terminal styling library (https://pypi.org/project/clr/). Therefore, we must first check if pythonnet is actually
# available...
from PyInstaller.utils.hooks import is_module_satisfies
from PyInstaller.compat import is_win

if is_module_satisfies("pythonnet"):
    # pythonnet requires both clr.pyd and Python.Runtime.dll, but the latter isn't found by PyInstaller.
    import ctypes.util
    from PyInstaller.log import logger

    try:
        import importlib.metadata as importlib_metadata
    except ImportError:
        import importlib_metadata

    collected_runtime_files = []

    # Try finding Python.Runtime.dll via distribution's file list
    dist_files = importlib_metadata.files('pythonnet')
    if dist_files is not None:
        runtime_dll_files = [f for f in dist_files if f.match('Python.Runtime.dll')]
        if len(runtime_dll_files) == 1:
            runtime_dll_file = runtime_dll_files[0]
            collected_runtime_files = [(runtime_dll_file.locate(), runtime_dll_file.parent.as_posix())]
            logger.debug("hook-clr: Python.Runtime.dll discovered via metadata.")
        elif len(runtime_dll_files) > 1:
            logger.warning("hook-clr: multiple instances of Python.Runtime.dll listed in metadata - cannot resolve.")

    # Fall back to the legacy way
    if not collected_runtime_files:
        runtime_dll_file = ctypes.util.find_library('Python.Runtime')
        if runtime_dll_file:
            collected_runtime_files = [(runtime_dll_file, '.')]
            logger.debug('hook-clr: Python.Runtime.dll discovered via legacy method.')

    if not collected_runtime_files:
        raise Exception('Python.Runtime.dll not found')

    # On Windows, collect runtime DLL file(s) as binaries; on other OSes, collect them as data files, to prevent fatal
    # errors in binary dependency analysis.
    if is_win:
        binaries = collected_runtime_files
    else:
        datas = collected_runtime_files

    # These modules are imported inside Python.Runtime.dll
    hiddenimports = ["platform", "warnings"]
