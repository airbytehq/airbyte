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

import os

from PyInstaller import compat
from PyInstaller import isolated
from PyInstaller import log as logging
from PyInstaller.building.datastruct import Tree
from PyInstaller.depend import bindepend

logger = logging.getLogger(__name__)

TK_ROOTNAME = 'tk'
TCL_ROOTNAME = 'tcl'


@isolated.decorate
def _get_tcl_tk_info():
    """
    Isolated-subprocess helper to retrieve the basic Tcl/Tk information:
     - tcl_dir = path to the Tcl library/data directory.
     - tcl_version = Tcl version
     - tk_version = Tk version
     - tcl_theaded = boolean indicating whether Tcl/Tk is built with multi-threading support.
    """
    try:
        import tkinter
        from _tkinter import TCL_VERSION, TK_VERSION
    except ImportError:
        # tkinter unavailable
        return None, None, None, False
    try:
        tcl = tkinter.Tcl()
    except tkinter.TclError:  # e.g. "Can't find a usable init.tcl in the following directories: ..."
        return None, None, None, False

    # Query the location of Tcl library/data directory.
    tcl_dir = tcl.eval("info library")

    # Check if Tcl/Tk is built with multi-threaded support (built with --enable-threads), as indicated by the presence
    # of optional `threaded` member in `tcl_platform` array.
    try:
        tcl.getvar("tcl_platform(threaded)")  # Ignore the actual value.
        tcl_threaded = True
    except tkinter.TclError:
        tcl_threaded = False

    return tcl_dir, TCL_VERSION, TK_VERSION, tcl_threaded


# Populate the variables. If `tkinter` is unavailable, the values are set to `None` or `False`.
(
    tcl_dir,
    tcl_version,
    tk_version,
    tcl_threaded,
) = _get_tcl_tk_info()


def _warn_if_activetcl_or_teapot_installed(tcl_root, tcltree):
    """
    If the current Tcl installation is a Teapot-distributed version of ActiveTcl *and* the current platform is macOS,
    log a non-fatal warning that the resulting executable will (probably) fail to run on non-host systems.

    PyInstaller does *not* freeze all ActiveTcl dependencies -- including Teapot, which is typically ignorable. Since
    Teapot is *not* ignorable in this case, this function warns of impending failure.

    See Also
    -------
    https://github.com/pyinstaller/pyinstaller/issues/621
    """
    import macholib.util

    # System libraries do not experience this problem.
    if macholib.util.in_system_path(tcl_root):
        return

    # Absolute path of the "init.tcl" script.
    try:
        init_resource = [r[1] for r in tcltree if r[1].endswith('init.tcl')][0]
    except IndexError:
        # If such script could not be found, silently return.
        return

    mentions_activetcl = False
    mentions_teapot = False
    # TCL/TK reads files using the system encoding:
    # https://www.tcl.tk/doc/howto/i18n.html#system_encoding
    # On macOS, system encoding is UTF-8
    with open(init_resource, 'r', encoding='utf8') as init_file:
        for line in init_file.readlines():
            line = line.strip().lower()
            if line.startswith('#'):
                continue
            if 'activetcl' in line:
                mentions_activetcl = True
            if 'teapot' in line:
                mentions_teapot = True
            if mentions_activetcl and mentions_teapot:
                break

    if mentions_activetcl and mentions_teapot:
        logger.warning(
            """
You appear to be using an ActiveTcl build of Tcl/Tk, which PyInstaller has
difficulty freezing. To fix this, comment out all references to "teapot" in:

     %s

See https://github.com/pyinstaller/pyinstaller/issues/621 for more information.
            """ % init_resource
        )


def find_tcl_tk_shared_libs(tkinter_ext_file):
    """
    Find Tcl and Tk shared libraries against which the _tkinter module is linked.

    Returns
    -------
    list
        list containing two tuples, one for Tcl and one for Tk library, where each tuple contains the library name and
        its full path, i.e., [(tcl_lib, tcl_libpath), (tk_lib, tk_libpath)]. If a library is not found, the
        corresponding tuple elements are set to None.
    """
    tcl_lib = None
    tcl_libpath = None
    tk_lib = None
    tk_libpath = None

    for _, lib_path in bindepend.get_imports(tkinter_ext_file):  # (name, fullpath) tuple
        if lib_path is None:
            continue  # Skip unresolved entries

        # For comparison, take basename of lib_path. On macOS, lib_name returned by get_imports is in fact referenced
        # name, which is not necessarily just a basename.
        lib_name = os.path.basename(lib_path)
        lib_name_lower = lib_name.lower()  # lower-case for comparisons

        if 'tcl' in lib_name_lower:
            tcl_lib = lib_name
            tcl_libpath = lib_path
        elif 'tk' in lib_name_lower:
            tk_lib = lib_name
            tk_libpath = lib_path

    return [(tcl_lib, tcl_libpath), (tk_lib, tk_libpath)]


def _find_tcl_tk(tkinter_ext_file):
    """
    Get a platform-specific 2-tuple of the absolute paths of the top-level external data directories for both
    Tcl and Tk, respectively.

    Returns
    -------
    list
        2-tuple that contains the values of `${TCL_LIBRARY}` and `${TK_LIBRARY}`, respectively.
    """
    if compat.is_darwin:
        # On macOS, _tkinter extension is linked either against the system Tcl/Tk framework (older homebrew python,
        # python3 from XCode tools) or against bundled Tcl/Tk library (recent python.org builds, recent homebrew
        # python with python-tk). PyInstaller does not bundle data from system frameworks (as it does not not collect
        # shared libraries from them, either), so we need to determine what kind of Tcl/Tk we are dealing with.
        libs = find_tcl_tk_shared_libs(tkinter_ext_file)

        # Check the full path to the Tcl library.
        path_to_tcl = libs[0][1]

        # Starting with macOS 11, system libraries are hidden (unless both Python and PyInstaller's bootloader are built
        # against MacOS 11.x SDK). Therefore, libs may end up empty; but that implicitly indicates that the system
        # framework is used, so return (None, None) to inform the caller.
        if path_to_tcl is None:
            return None, None

        # Check if the path corresponds to the system framework, i.e., [/System]/Library/Frameworks/Tcl.framework/Tcl
        if 'Library/Frameworks/Tcl.framework' in path_to_tcl:
            return None, None  # Do not collect system framework's data.

        # Bundled copy of Tcl/Tk; in this case, the dynamic library is
        # /Library/Frameworks/Python.framework/Versions/3.x/lib/libtcl8.6.dylib
        # and the data directories have standard layout that is handled by code below.
    else:
        # On Windows and linux, data directories have standard layout that is handled by code below.
        pass

    # The Tcl library location is already stored in `tcl_dir` global variable. The Tk library is in the same prefix, so
    # construct the path using `tk_version` global variable.
    tk_dir = os.path.join(os.path.dirname(tcl_dir), f"tk{tk_version}")
    return tcl_dir, tk_dir


def _collect_tcl_modules(tcl_root):
    """
    Get a list of TOC-style 3-tuples describing Tcl modules. The modules directory is separate from the library/data
    one, and is located at $tcl_root/../tclX, where X is the major Tcl version.

    Returns
    -------
    Tree
        Such list, if the modules directory exists.
    """

    # Obtain Tcl major version.
    tcl_major_version = tcl_version.split('.')[0]

    modules_dirname = f"tcl{tcl_major_version}"
    modules_path = os.path.join(tcl_root, '..', modules_dirname)

    if not os.path.isdir(modules_path):
        logger.warning('Tcl modules directory %s does not exist.', modules_path)
        return []

    return Tree(modules_path, prefix=modules_dirname)


def collect_tcl_tk_files(tkinter_ext_file):
    """
    Get a list of TOC-style 3-tuples describing all external Tcl/Tk data files.

    Returns
    -------
    Tree
        Such list.
    """
    # Find Tcl and Tk data directory by analyzing the _tkinter extension.
    tcl_root, tk_root = _find_tcl_tk(tkinter_ext_file)

    # On macOS, we do not collect system libraries. Therefore, if system Tcl/Tk framework is used, it makes no sense to
    # collect its data, either. In this case, _find_tcl_tk() will return None, None - either deliberately (we found the
    # data paths, but ignore them) or not (starting with macOS 11, the data path cannot be found until shared library
    # discovery is fixed).
    if compat.is_darwin and not tcl_root and not tk_root:
        logger.info(
            "Not collecting Tcl/Tk data - either python is using macOS\' system Tcl/Tk framework, or Tcl/Tk data "
            "directories could not be found."
        )
        return []

    # TODO Shouldn't these be fatal exceptions?
    if not tcl_root:
        logger.error('Tcl/Tk improperly installed on this system.')
        return []
    if not os.path.isdir(tcl_root):
        logger.error('Tcl data directory "%s" not found.', tcl_root)
        return []
    if not os.path.isdir(tk_root):
        logger.error('Tk data directory "%s" not found.', tk_root)
        return []

    # Collect Tcl and Tk scripts from their corresponding library/data directories. In contrast to source directories,
    # which are typically versioned (tcl8.6, tk8.6), the target directories are unversioned (tcl, tk); they are added
    # to the Tcl/Tk search path via runtime hook for _tkinter, which sets the `TCL_LIBRARY` and `TK_LIBRARY` environment
    # variables.
    tcltree = Tree(tcl_root, prefix=TCL_ROOTNAME, excludes=['demos', '*.lib', 'tclConfig.sh'])
    tktree = Tree(tk_root, prefix=TK_ROOTNAME, excludes=['demos', '*.lib', 'tkConfig.sh'])

    # If the current Tcl installation is a Teapot-distributed version of ActiveTcl and the current platform is Mac OS,
    # warn that this is bad.
    if compat.is_darwin:
        _warn_if_activetcl_or_teapot_installed(tcl_root, tcltree)

    # Collect Tcl modules.
    tclmodulestree = _collect_tcl_modules(tcl_root)

    return tcltree + tktree + tclmodulestree
