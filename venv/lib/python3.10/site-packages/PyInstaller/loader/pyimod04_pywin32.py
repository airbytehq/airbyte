#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
"""
Set search path for pywin32 DLLs. Due to the large number of pywin32 modules, we use a single loader-level script
instead of per-module runtime hook scripts.
"""

import os
import sys


def install():
    # Sub-directories containing extensions. In original python environment, these are added to `sys.path` by the
    # `pywin32.pth` so the extensions end up treated as top-level modules. We attempt to preserve the directory
    # layout, so we need to add these directories to `sys.path` ourselves.
    pywin32_ext_paths = ('win32', 'pythonwin')
    pywin32_ext_paths = [os.path.join(sys._MEIPASS, pywin32_ext_path) for pywin32_ext_path in pywin32_ext_paths]
    pywin32_ext_paths = [path for path in pywin32_ext_paths if os.path.isdir(path)]
    sys.path.extend(pywin32_ext_paths)

    # Additional handling of `pywin32_system32` DLL directory
    pywin32_system32_path = os.path.join(sys._MEIPASS, 'pywin32_system32')

    if not os.path.isdir(pywin32_system32_path):
        # Either pywin32 is not collected, or we are dealing with version that does not use the pywin32_system32
        # sub-directory. In the latter case, the pywin32 DLLs should be in `sys._MEIPASS`, and nothing
        # else needs to be done here.
        return

    # Add the DLL directory to `sys.path`.
    # This is necessary because `__import_pywin32_system_module__` from `pywintypes` module assumes that in a frozen
    # application, the pywin32 DLLs (`pythoncom3X.dll` and `pywintypes3X.dll`) that are normally found in
    # `pywin32_system32` sub-directory in `sys.path` (site-packages, really) are located directly in `sys.path`.
    # This obviously runs afoul of our attempts at preserving the directory layout and placing them in the
    # `pywin32_system32` sub-directory instead of the top-level application directory.
    sys.path.append(pywin32_system32_path)

    # Add the DLL directory to DLL search path using os.add_dll_directory().
    # This allows extensions from win32 directory (e.g., win32api, win32crypt) to be loaded on their own without
    # importing pywintypes first. The extensions are linked against pywintypes3X.dll.
    os.add_dll_directory(pywin32_system32_path)

    # Add the DLL directory to PATH. This is necessary under certain versions of
    # Anaconda python, where `os.add_dll_directory` does not work.
    path = os.environ.get('PATH', None)
    if not path:
        path = pywin32_system32_path
    else:
        path = pywin32_system32_path + os.pathsep + path
    os.environ['PATH'] = path
