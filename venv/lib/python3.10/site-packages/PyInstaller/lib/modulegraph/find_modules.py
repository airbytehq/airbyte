"""
modulegraph.find_modules - High-level module dependency finding interface
=========================================================================

History
........

Originally (loosely) based on code in py2exe's build_exe.py by Thomas Heller.
"""
import os
import pkgutil

from .modulegraph import Alias

def get_implies():
    def _xml_etree_modules():
        import xml.etree
        return [
            f"xml.etree.{module_name}"
            for _, module_name, is_package in pkgutil.iter_modules(xml.etree.__path__)
            if not is_package
        ]

    result = {
        # imports done from C code in built-in and/or extension modules
        # (untrackable by modulegraph).
        "_curses": ["curses"],
        "posix": ["resource"],
        "gc": ["time"],
        "time": ["_strptime"],
        "datetime": ["time"],
        "parser": ["copyreg"],
        "codecs": ["encodings"],
        "_sre": ["copy", "re"],
        "zipimport": ["zlib"],

        # _frozen_importlib is part of the interpreter itself
        "_frozen_importlib": None,

        # os.path is an alias for a platform specific module,
        # ensure that the graph shows this.
        "os.path": Alias(os.path.__name__),

        # Python >= 3.2:
        "_datetime": ["time", "_strptime"],
        "_json": ["json.decoder"],
        "_pickle": ["codecs", "copyreg", "_compat_pickle"],
        "_posixsubprocess": ["gc"],
        "_ssl": ["socket"],

        # Python >= 3.3:
        "_elementtree": ["pyexpat"] + _xml_etree_modules(),

        # This is not C extension, but it uses __import__
        "anydbm": ["dbhash", "gdbm", "dbm", "dumbdbm", "whichdb"],

        # Known package aliases
        "wxPython.wx": Alias('wx'),
    }

    return result
