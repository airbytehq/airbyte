#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
"""
Hooks to make ctypes.CDLL, .PyDLL, etc. look in sys._MEIPASS first.
"""

import sys


def install():
    """
    Install the hooks.

    This must be done from a function as opposed to at module-level, because when the module is imported/executed,
    the import machinery is not completely set up yet.
    """

    import os

    try:
        import ctypes
    except ImportError:
        # ctypes is not included in the frozen application
        return

    def _frozen_name(name):
        # If the given (file)name does not exist, fall back to searching for its basename in sys._MEIPASS, where
        # PyInstaller usually collects shared libraries.
        if name and not os.path.isfile(name):
            frozen_name = os.path.join(sys._MEIPASS, os.path.basename(name))
            if os.path.isfile(frozen_name):
                name = frozen_name
        return name

    class PyInstallerImportError(OSError):
        def __init__(self, name):
            self.msg = (
                "Failed to load dynlib/dll %r. Most likely this dynlib/dll was not found when the application "
                "was frozen." % name
            )
            self.args = (self.msg,)

    class PyInstallerCDLL(ctypes.CDLL):
        def __init__(self, name, *args, **kwargs):
            name = _frozen_name(name)
            try:
                super().__init__(name, *args, **kwargs)
            except Exception as base_error:
                raise PyInstallerImportError(name) from base_error

    ctypes.CDLL = PyInstallerCDLL
    ctypes.cdll = ctypes.LibraryLoader(PyInstallerCDLL)

    class PyInstallerPyDLL(ctypes.PyDLL):
        def __init__(self, name, *args, **kwargs):
            name = _frozen_name(name)
            try:
                super().__init__(name, *args, **kwargs)
            except Exception as base_error:
                raise PyInstallerImportError(name) from base_error

    ctypes.PyDLL = PyInstallerPyDLL
    ctypes.pydll = ctypes.LibraryLoader(PyInstallerPyDLL)

    if sys.platform.startswith('win'):

        class PyInstallerWinDLL(ctypes.WinDLL):
            def __init__(self, name, *args, **kwargs):
                name = _frozen_name(name)
                try:
                    super().__init__(name, *args, **kwargs)
                except Exception as base_error:
                    raise PyInstallerImportError(name) from base_error

        ctypes.WinDLL = PyInstallerWinDLL
        ctypes.windll = ctypes.LibraryLoader(PyInstallerWinDLL)

        class PyInstallerOleDLL(ctypes.OleDLL):
            def __init__(self, name, *args, **kwargs):
                name = _frozen_name(name)
                try:
                    super().__init__(name, *args, **kwargs)
                except Exception as base_error:
                    raise PyInstallerImportError(name) from base_error

        ctypes.OleDLL = PyInstallerOleDLL
        ctypes.oledll = ctypes.LibraryLoader(PyInstallerOleDLL)

        try:
            import ctypes.util
        except ImportError:
            # ctypes.util is not included in the frozen application
            return

        # Same implementation as ctypes.util.find_library, except it prepends sys._MEIPASS to the search directories.
        def pyinstaller_find_library(name):
            if name in ('c', 'm'):
                return ctypes.util.find_msvcrt()
            # See MSDN for the REAL search order.
            search_dirs = [sys._MEIPASS] + os.environ['PATH'].split(os.pathsep)
            for directory in search_dirs:
                fname = os.path.join(directory, name)
                if os.path.isfile(fname):
                    return fname
                if fname.lower().endswith(".dll"):
                    continue
                fname = fname + ".dll"
                if os.path.isfile(fname):
                    return fname
            return None

        ctypes.util.find_library = pyinstaller_find_library


# On Mac OS insert sys._MEIPASS in the first position of the list of paths that ctypes uses to search for libraries.
#
# Note: 'ctypes' module will NOT be bundled with every app because code in this module is not scanned for module
#       dependencies. It is safe to wrap 'ctypes' module into 'try/except ImportError' block.
if sys.platform.startswith('darwin'):
    try:
        from ctypes.macholib import dyld
        dyld.DEFAULT_LIBRARY_FALLBACK.insert(0, sys._MEIPASS)
    except ImportError:
        # Do nothing when module 'ctypes' is not available.
        pass
