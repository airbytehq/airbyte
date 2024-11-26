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
"""
Build packages using spec files.

NOTE: All global variables, classes and imported modules create API for .spec files.
"""

import glob
import os
import pathlib
import pprint
import shutil
import enum

import sys

from PyInstaller import DEFAULT_DISTPATH, DEFAULT_WORKPATH, HOMEPATH, compat
from PyInstaller import log as logging
from PyInstaller.building.api import COLLECT, EXE, MERGE, PYZ
from PyInstaller.building.datastruct import (
    TOC, Target, Tree, _check_guts_eq, normalize_toc, normalize_pyz_toc, toc_process_symbolic_links
)
from PyInstaller.building.osx import BUNDLE
from PyInstaller.building.splash import Splash
from PyInstaller.building.utils import (
    _check_guts_toc, _check_guts_toc_mtime, _should_include_system_binary, format_binaries_and_datas, compile_pymodule,
    add_suffix_to_extension, postprocess_binaries_toc_pywin32, postprocess_binaries_toc_pywin32_anaconda
)
from PyInstaller.compat import is_win, is_conda, is_darwin
from PyInstaller.depend import bindepend
from PyInstaller.depend.analysis import initialize_modgraph
from PyInstaller.depend.utils import create_py3_base_library, scan_code_for_ctypes
from PyInstaller import isolated
from PyInstaller.utils.misc import absnormpath, get_path_to_toplevel_modules, mtime
from PyInstaller.utils.hooks import get_package_paths
from PyInstaller.utils.hooks.gi import compile_glib_schema_files

if is_darwin:
    from PyInstaller.utils import osx as osxutils

logger = logging.getLogger(__name__)

STRINGTYPE = type('')
TUPLETYPE = type((None,))

rthooks = {}

# Place where the loader modules and initialization scripts live.
_init_code_path = os.path.join(HOMEPATH, 'PyInstaller', 'loader')

IMPORT_TYPES = [
    'top-level', 'conditional', 'delayed', 'delayed, conditional', 'optional', 'conditional, optional',
    'delayed, optional', 'delayed, conditional, optional'
]

WARNFILE_HEADER = """\

This file lists modules PyInstaller was not able to find. This does not
necessarily mean this module is required for running your program. Python and
Python 3rd-party packages include a lot of conditional or optional modules. For
example the module 'ntpath' only exists on Windows, whereas the module
'posixpath' only exists on Posix systems.

Types if import:
* top-level: imported at the top-level - look at these first
* conditional: imported within an if-statement
* delayed: imported within a function
* optional: imported within a try-except-statement

IMPORTANT: Do NOT post this list to the issue-tracker. Use it as a basis for
            tracking down the missing module yourself. Thanks!

"""


@isolated.decorate
def discover_hook_directories():
    """
    Discover hook directories via pyinstaller40 entry points. Perform the discovery in an isolated subprocess
    to avoid importing the package(s) in the main process.

    :return: list of discovered hook directories.
    """

    from traceback import format_exception_only
    from PyInstaller.log import logger
    from PyInstaller.compat import importlib_metadata

    # The “selectable” entry points (via group and name keyword args) were introduced in importlib_metadata 4.6 and
    # Python 3.10. The compat module ensures we are using a compatible version.
    entry_points = importlib_metadata.entry_points(group='pyinstaller40', name='hook-dirs')

    # Ensure that pyinstaller_hooks_contrib comes last so that hooks from packages providing their own take priority.
    entry_points = sorted(entry_points, key=lambda x: x.module == "_pyinstaller_hooks_contrib.hooks")

    hook_directories = []
    for entry_point in entry_points:
        try:
            hook_directories.extend(entry_point.load()())
        except Exception as e:
            msg = "".join(format_exception_only(type(e), e)).strip()
            logger.warning("discover_hook_directories: Failed to process hook entry point '%s': %s", entry_point, msg)

    logger.debug("discover_hook_directories: Hook directories: %s", hook_directories)

    return hook_directories


def find_binary_dependencies(binaries, import_packages):
    """
    Find dynamic dependencies (linked shared libraries) for the provided list of binaries.

    On Windows, this function performs additional pre-processing in an isolated environment in an attempt to handle
    dynamic library search path modifications made by packages during their import. The packages from the given list
    of collected packages are imported one by one, while keeping track of modifications made by `os.add_dll_directory`
    calls and additions to the `PATH`  environment variable. The recorded additional search paths are then passed to
    the binary dependency analysis step.

    binaries
            List of binaries to scan for dynamic dependencies.
    import_packages
            List of packages to import prior to scanning binaries.

    :return: expanded list of binaries and then dependencies.
    """

    # Extra library search paths (used on Windows to resolve DLL paths).
    extra_libdirs = []
    if compat.is_win:
        # Always search `sys.base_prefix`, and search it first. This ensures that we resolve the correct version of
        # `python3X.dll` and `python3.dll` (a PEP-0384 stable ABI stub that forwards symbols to the fully versioned
        # `python3X.dll`), regardless of other python installations that might be present in the PATH.
        extra_libdirs.append(compat.base_prefix)

        # If `pywin32` is installed, resolve the path to the `pywin32_system32` directory. Most `pywin32` extensions
        # reference the `pywintypes3X.dll` in there. Based on resolved `pywin32_system32` directory, also add other
        # `pywin32` directory, in case extensions in different directories reference each other (the ones in the same
        # directory should already be resolvable due to binary dependency analysis passing the analyzed binary's
        # location to the `get_imports` function). This allows us to avoid searching all paths in `sys.path`, which
        # may lead to other corner-case issues (e.g., #5560).
        pywin32_system32_dir = None
        try:
            # Look up the directory by treating it as a namespace package.
            _, pywin32_system32_dir = get_package_paths('pywin32_system32')
        except Exception:
            pass

        if pywin32_system32_dir:
            pywin32_base_dir = os.path.dirname(pywin32_system32_dir)
            extra_libdirs += [
                pywin32_system32_dir,  # .../pywin32_system32
                # based on pywin32.pth
                os.path.join(pywin32_base_dir, 'win32'),  # .../win32
                os.path.join(pywin32_base_dir, 'win32', 'lib'),  # .../win32/lib
                os.path.join(pywin32_base_dir, 'Pythonwin'),  # .../Pythonwin
            ]

    # On Windows, packages' initialization code might register additional DLL search paths, either by modifying the
    # `PATH` environment variable, or by calling `os.add_dll_directory`. Therefore, we import all collected packages,
    # and track changes made to the environment.
    if compat.is_win:
        # Helper functions to be executed in isolated environment.
        def setup():
            """
            Prepare environment for change tracking
            """
            import os

            os._added_dll_directories = []
            os._original_path_env = os.environ.get('PATH', '')

            _original_add_dll_directory = os.add_dll_directory

            def _pyi_add_dll_directory(path):
                os._added_dll_directories.append(path)
                return _original_add_dll_directory(path)

            os.add_dll_directory = _pyi_add_dll_directory

        def import_library(package):
            """
            Import collected package to set up environment.
            """
            try:
                __import__(package)
            except Exception:
                pass

        def process_search_paths():
            """
            Obtain lists of added search paths.
            """
            import os

            # `os.add_dll_directory` might be called with a `pathlib.Path`, which cannot be marhsalled out of the helper
            # process. So explicitly convert all entries to strings.
            dll_directories = [str(path) for path in os._added_dll_directories]

            orig_path = set(os._original_path_env.split(os.pathsep))
            modified_path = os.environ.get('PATH', '').split(os.pathsep)
            path_additions = [path for path in modified_path if path and path not in orig_path]

            return dll_directories, path_additions

        # Processing in isolated environment.
        with isolated.Python() as child:
            child.call(setup)
            for package in import_packages:
                child.call(import_library, package)
            added_dll_directories, added_path_directories = child.call(process_search_paths)

        # Process extra search paths...
        logger.info("Extra DLL search directories (AddDllDirectory): %r", added_dll_directories)
        extra_libdirs += added_dll_directories

        logger.info("Extra DLL search directories (PATH): %r", added_path_directories)
        extra_libdirs += added_path_directories

    # Deduplicate search paths
    # NOTE: `list(set(extra_libdirs))` does not preserve the order of search paths (which matters here), so we need to
    # de-duplicate using `list(dict.fromkeys(extra_libdirs).keys())` instead.
    extra_libdirs = list(dict.fromkeys(extra_libdirs).keys())

    # Search for dependencies of the given binaries
    return bindepend.binary_dependency_analysis(binaries, search_paths=extra_libdirs)


class _ModuleCollectionMode(enum.IntFlag):
    """
    Module collection mode flags.
    """
    PYZ = enum.auto()  # Collect byte-compiled .pyc into PYZ archive
    PYC = enum.auto()  # Collect byte-compiled .pyc as external data file
    PY = enum.auto()  # Collect source .py file as external data file


_MODULE_COLLECTION_MODES = {
    "pyz": _ModuleCollectionMode.PYZ,
    "pyc": _ModuleCollectionMode.PYC,
    "py": _ModuleCollectionMode.PY,
    "pyz+py": _ModuleCollectionMode.PYZ | _ModuleCollectionMode.PY,
    "py+pyz": _ModuleCollectionMode.PYZ | _ModuleCollectionMode.PY,
}


def _get_module_collection_mode(mode_dict, name, noarchive=False):
    """
    Determine the module/package collection mode for the given module name, based on the provided collection
    mode settings dictionary.
    """
    # Default mode: collect into PYZ, unless noarchive is enabled. In that case, collect as pyc.
    mode_flags = _ModuleCollectionMode.PYC if noarchive else _ModuleCollectionMode.PYZ

    # If we have no collection mode settings, end here and now.
    if not mode_dict:
        return mode_flags

    # Search the parent modules/packages in top-down fashion, and take the last given setting. This ensures that
    # a setting given for the top-level package is recursively propagated to all its subpackages and submodules,
    # but also allows individual sub-modules to override the setting again.
    mode = 'pyz'

    name_parts = name.split('.')
    for i in range(len(name_parts)):
        modlevel = ".".join(name_parts[:i + 1])
        modlevel_mode = mode_dict.get(modlevel, None)
        if modlevel_mode is not None:
            mode = modlevel_mode

    # Convert mode string to _ModuleCollectionMode flags
    try:
        mode_flags = _MODULE_COLLECTION_MODES[mode]
    except KeyError:
        raise ValueError(f"Unknown module collection mode for {name!r}: {mode!r}!")

    # noarchive flag being set means that we need to change _ModuleCollectionMode.PYZ into _ModuleCollectionMode.PYC
    if noarchive and _ModuleCollectionMode.PYZ in mode_flags:
        mode_flags ^= _ModuleCollectionMode.PYZ
        mode_flags |= _ModuleCollectionMode.PYC

    return mode_flags


class Analysis(Target):
    """
    Class that performs analysis of the user's main Python scripts.

    An Analysis contains multiple TOC (Table of Contents) lists, accessed as attributes of the analysis object.

    scripts
            The scripts you gave Analysis as input, with any runtime hook scripts prepended.
    pure
            The pure Python modules.
    binaries
            The extension modules and their dependencies.
    datas
            Data files collected from packages.
    zipfiles
            Deprecated - always empty.
    zipped_data
            Deprecated - always empty.
    """
    _old_scripts = {
        absnormpath(os.path.join(HOMEPATH, "support", "_mountzlib.py")),
        absnormpath(os.path.join(HOMEPATH, "support", "useUnicode.py")),
        absnormpath(os.path.join(HOMEPATH, "support", "useTK.py")),
        absnormpath(os.path.join(HOMEPATH, "support", "unpackTK.py")),
        absnormpath(os.path.join(HOMEPATH, "support", "removeTK.py"))
    }

    def __init__(
        self,
        scripts,
        pathex=None,
        binaries=None,
        datas=None,
        hiddenimports=None,
        hookspath=None,
        hooksconfig=None,
        excludes=None,
        runtime_hooks=None,
        cipher=None,
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        noarchive=False,
        module_collection_mode=None,
        **_kwargs,
    ):
        """
        scripts
                A list of scripts specified as file names.
        pathex
                An optional list of paths to be searched before sys.path.
        binaries
                An optional list of additional binaries (dlls, etc.) to include.
        datas
                An optional list of additional data files to include.
        hiddenimport
                An optional list of additional (hidden) modules to include.
        hookspath
                An optional list of additional paths to search for hooks. (hook-modules).
        hooksconfig
                An optional dict of config settings for hooks. (hook-modules).
        excludes
                An optional list of module or package names (their Python names, not path names) that will be
                ignored (as though they were not found).
        runtime_hooks
                An optional list of scripts to use as users' runtime hooks. Specified as file names.
        cipher
                Deprecated. Raises an error if not None.
        win_no_prefer_redirects
                Deprecated. Raises an error if not False.
        win_private_assemblies
                Deprecated. Raises an error if not False.
        noarchive
                If True, do not place source files in a archive, but keep them as individual files.
        module_collection_mode
                An optional dict of package/module names and collection mode strings. Valid collection mode strings:
                'pyz' (default), 'pyc', 'py', 'pyz+py' (or 'py+pyz')
        """
        if cipher is not None:
            from PyInstaller.exceptions import RemovedCipherFeatureError
            raise RemovedCipherFeatureError(
                "Please remove the 'cipher' arguments to PYZ() and Analysis() in your spec file."
            )
        if win_no_prefer_redirects:
            from PyInstaller.exceptions import RemovedWinSideBySideSupportError
            raise RemovedWinSideBySideSupportError(
                "Please remove the 'win_no_prefer_redirects' argument to Analysis() in your spec file."
            )
        if win_private_assemblies:
            from PyInstaller.exceptions import RemovedWinSideBySideSupportError
            raise RemovedWinSideBySideSupportError(
                "Please remove the 'win_private_assemblies' argument to Analysis() in your spec file."
            )
        super().__init__()
        from PyInstaller.config import CONF

        self.inputs = []
        spec_dir = os.path.dirname(CONF['spec'])
        for script in scripts:
            # If path is relative, it is relative to the location of .spec file.
            if not os.path.isabs(script):
                script = os.path.join(spec_dir, script)
            if absnormpath(script) in self._old_scripts:
                logger.warning('Ignoring obsolete auto-added script %s', script)
                continue
            # Normalize script path.
            script = os.path.normpath(script)
            if not os.path.exists(script):
                raise SystemExit("script '%s' not found" % script)
            self.inputs.append(script)

        # Django hook requires this variable to find the script manage.py.
        CONF['main_script'] = self.inputs[0]

        self.pathex = self._extend_pathex(pathex, self.inputs)
        # Set global config variable 'pathex' to make it available for PyInstaller.utils.hooks and import hooks. Path
        # extensions for module search.
        CONF['pathex'] = self.pathex
        # Extend sys.path so PyInstaller could find all necessary modules.
        logger.info('Extending PYTHONPATH with paths\n' + pprint.pformat(self.pathex))
        sys.path.extend(self.pathex)

        self.hiddenimports = hiddenimports or []
        # Include hidden imports passed via CONF['hiddenimports']; these might be populated if user has a wrapper script
        # that calls `build_main.main()` with custom `pyi_config` dictionary that contains `hiddenimports`.
        self.hiddenimports.extend(CONF.get('hiddenimports', []))

        self.hookspath = []
        # Append directories in `hookspath` (`--additional-hooks-dir`) to take precedence over those from the entry
        # points.
        if hookspath:
            self.hookspath.extend(hookspath)

        # Add hook directories from PyInstaller entry points.
        self.hookspath += discover_hook_directories()

        self.hooksconfig = {}
        if hooksconfig:
            self.hooksconfig.update(hooksconfig)

        # Custom runtime hook files that should be included and started before any existing PyInstaller runtime hooks.
        self.custom_runtime_hooks = runtime_hooks or []

        self._input_binaries = []
        self._input_datas = []

        self.excludes = excludes or []
        self.scripts = []
        self.pure = []
        self.binaries = []
        self.zipfiles = []
        self.zipped_data = []
        self.datas = []
        self.dependencies = []
        self._python_version = sys.version
        self.noarchive = noarchive
        self.module_collection_mode = module_collection_mode or {}

        # Expand the `binaries` and `datas` lists specified in the .spec file, and ensure that the lists are normalized
        # and sorted before guts comparison.
        #
        # While we use these lists to initialize `Analysis.binaries` and `Analysis.datas`, at this point, we need to
        # store them in separate variables, which undergo *full* guts comparison (`_check_guts_toc`) as opposed to
        # just mtime-based comparison (`_check_guts_toc_mtime`). Changes to these initial list *must* trigger a rebuild
        # (and due to the way things work, a re-analysis), otherwise user might end up with a cached build that fails to
        # reflect the changes.
        if binaries:
            logger.info("Appending 'binaries' from .spec")
            self._input_binaries = [(dest_name, src_name, 'BINARY')
                                    for dest_name, src_name in format_binaries_and_datas(binaries, workingdir=spec_dir)]
            self._input_binaries = sorted(normalize_toc(self._input_binaries))

        if datas:
            logger.info("Appending 'datas' from .spec")
            self._input_datas = [(dest_name, src_name, 'DATA')
                                 for dest_name, src_name in format_binaries_and_datas(datas, workingdir=spec_dir)]
            self._input_datas = sorted(normalize_toc(self._input_datas))

        self.__postinit__()

    _GUTS = (  # input parameters
        ('inputs', _check_guts_eq),  # parameter `scripts`
        ('pathex', _check_guts_eq),
        ('hiddenimports', _check_guts_eq),
        ('hookspath', _check_guts_eq),
        ('hooksconfig', _check_guts_eq),
        ('excludes', _check_guts_eq),
        ('custom_runtime_hooks', _check_guts_eq),
        ('noarchive', _check_guts_eq),
        ('module_collection_mode', _check_guts_eq),

        ('_input_binaries', _check_guts_toc),
        ('_input_datas', _check_guts_toc),

        # calculated/analysed values
        ('_python_version', _check_guts_eq),
        ('scripts', _check_guts_toc_mtime),
        ('pure', _check_guts_toc_mtime),
        ('binaries', _check_guts_toc_mtime),
        ('zipfiles', _check_guts_toc_mtime),
        ('zipped_data', None),  # TODO check this, too
        ('datas', _check_guts_toc_mtime),
        # TODO: Need to add "dependencies"?
    )

    def _extend_pathex(self, spec_pathex, scripts):
        """
        Normalize additional paths where PyInstaller will look for modules and add paths with scripts to the list of
        paths.

        :param spec_pathex: Additional paths defined defined in .spec file.
        :param scripts: Scripts to create executable from.
        :return: list of updated paths
        """
        # Based on main supplied script - add top-level modules directory to PYTHONPATH.
        # Sometimes the main app script is not top-level module but submodule like 'mymodule.mainscript.py'.
        # In that case PyInstaller will not be able find modules in the directory containing 'mymodule'.
        # Add this directory to PYTHONPATH so PyInstaller could find it.
        pathex = []
        # Add scripts paths first.
        for script in scripts:
            logger.debug('script: %s' % script)
            script_toplevel_dir = get_path_to_toplevel_modules(script)
            if script_toplevel_dir:
                pathex.append(script_toplevel_dir)
        # Append paths from .spec.
        if spec_pathex is not None:
            pathex.extend(spec_pathex)
        # Normalize paths in pathex and make them absolute.
        return [absnormpath(p) for p in pathex]

    def _check_guts(self, data, last_build):
        if Target._check_guts(self, data, last_build):
            return True
        for filename in self.inputs:
            if mtime(filename) > last_build:
                logger.info("Building because %s changed", filename)
                return True
        # Now we know that none of the input parameters and none of the input files has changed. So take the values
        # that were calculated / analyzed in the last run and store them in `self`. These TOC lists should already
        # be normalized.
        self.scripts = data['scripts']
        self.pure = data['pure']
        self.binaries = data['binaries']
        self.zipfiles = data['zipfiles']
        self.zipped_data = data['zipped_data']
        self.datas = data['datas']

        return False

    def assemble(self):
        """
        This method is the MAIN method for finding all necessary files to be bundled.
        """
        from PyInstaller.config import CONF

        for m in self.excludes:
            logger.debug("Excluding module '%s'" % m)
        self.graph = initialize_modgraph(excludes=self.excludes, user_hook_dirs=self.hookspath)

        # Initialize `binaries` and `datas` with `_input_binaries` and `_input_datas`. Make sure to copy the lists
        # to prevent modifications of original lists, which we need to store in original form for guts comparison.
        self.datas = [entry for entry in self._input_datas]
        self.binaries = [entry for entry in self._input_binaries]

        # TODO: find a better place where to put 'base_library.zip' and when to created it.
        # For Python 3 it is necessary to create file 'base_library.zip' containing core Python modules. In Python 3
        # some built-in modules are written in pure Python. base_library.zip is a way how to have those modules as
        # "built-in".
        libzip_filename = os.path.join(CONF['workpath'], 'base_library.zip')
        create_py3_base_library(libzip_filename, graph=self.graph)
        # Bundle base_library.zip as data file.
        # Data format of TOC item: ('relative_path_in_dist_dir', 'absolute_path_on_disk', 'DATA')
        self.datas.append((os.path.basename(libzip_filename), libzip_filename, 'DATA'))

        # Expand sys.path of module graph. The attribute is the set of paths to use for imports: sys.path, plus our
        # loader, plus other paths from e.g. --path option).
        self.graph.path = self.pathex + self.graph.path

        # Scan for legacy namespace packages.
        self.graph.scan_legacy_namespace_packages()

        logger.info("Running Analysis %s", self.tocbasename)

        # Search for python shared library, which we need to collect into frozen application.
        logger.info('Looking for Python shared library...')
        python_lib = bindepend.get_python_library_path()
        if python_lib is None:
            from PyInstaller.exceptions import PythonLibraryNotFoundError
            raise PythonLibraryNotFoundError()
        logger.info('Using Python shared library: %s', python_lib)
        if is_darwin and osxutils.is_framework_bundle_lib(python_lib):
            # If python library is located in macOS .framework bundle, collect the bundle, and create symbolic link to
            # top-level directory.
            src_path = pathlib.PurePath(python_lib)
            dst_path = pathlib.PurePath(src_path.relative_to(src_path.parent.parent.parent.parent))
            self.binaries.append((str(dst_path), str(src_path), 'BINARY'))
            self.binaries.append((os.path.basename(python_lib), str(dst_path), 'SYMLINK'))
        else:
            self.binaries.append((os.path.basename(python_lib), python_lib, 'BINARY'))

        # -- Module graph. --
        #
        # Construct the module graph of import relationships between modules required by this user's application. For
        # each entry point (top-level user-defined Python script), all imports originating from this entry point are
        # recursively parsed into a subgraph of the module graph. This subgraph is then connected to this graph's root
        # node, ensuring imported module nodes will be reachable from the root node -- which is is (arbitrarily) chosen
        # to be the first entry point's node.

        # List to hold graph nodes of scripts and runtime hooks in use order.
        priority_scripts = []

        # Assume that if the script does not exist, Modulegraph will raise error. Save the graph nodes of each in
        # sequence.
        for script in self.inputs:
            logger.info("Analyzing %s", script)
            priority_scripts.append(self.graph.add_script(script))

        # Analyze the script's hidden imports (named on the command line)
        self.graph.add_hiddenimports(self.hiddenimports)

        # -- Post-graph hooks. --
        self.graph.process_post_graph_hooks(self)

        # Update 'binaries' and 'datas' TOC lists with entries collected from hooks.
        self.binaries += self.graph.make_hook_binaries_toc()
        self.datas += self.graph.make_hook_datas_toc()

        # We do not support zipped eggs anymore (PyInstaller v6.0), so `zipped_data` and `zipfiles` are always empty.
        self.zipped_data = []
        self.zipfiles = []

        # -- Automatic binary vs. data reclassification. --
        #
        # At this point, `binaries` and `datas` contain  TOC entries supplied by user via input arguments, and by hooks
        # that were ran during the analysis. Neither source can be fully trusted regarding the DATA vs BINARY
        # classification (no thanks to our hookutils not being 100% reliable, either!). Therefore, inspect the files and
        # automatically reclassify them as necessary.
        #
        # The proper classification is important especially for collected binaries - to ensure that they undergo binary
        # dependency analysis and platform-specific binary processing. On macOS, the .app bundle generation code also
        # depends on files to be properly classified.
        #
        # For entries added to `binaries` and `datas` after this point, we trust their typecodes due to the nature of
        # their origin.
        combined_toc = normalize_toc(self.datas + self.binaries)

        logger.info('Performing binary vs. data reclassification (%d entries)', len(combined_toc))

        self.datas = []
        self.binaries = []

        for dest_name, src_name, typecode in combined_toc:
            # Returns 'BINARY' or 'DATA', or None if file cannot be classified.
            detected_typecode = bindepend.classify_binary_vs_data(src_name)
            if detected_typecode is not None:
                if detected_typecode != typecode:
                    logger.debug(
                        "Reclassifying collected file %r from %s to %s...", src_name, typecode, detected_typecode
                    )
                typecode = detected_typecode

            # Put back into corresponding TOC list.
            if typecode in {'BINARY', 'EXTENSION'}:
                self.binaries.append((dest_name, src_name, typecode))
            else:
                self.datas.append((dest_name, src_name, typecode))

        # -- Look for dlls that are imported by Python 'ctypes' module. --
        # First get code objects of all modules that import 'ctypes'.
        logger.info('Looking for ctypes DLLs')
        # dict like: {'module1': code_obj, 'module2': code_obj}
        ctypes_code_objs = self.graph.get_code_using("ctypes")

        for name, co in ctypes_code_objs.items():
            # Get dlls that might be needed by ctypes.
            logger.debug('Scanning %s for ctypes-based references to shared libraries', name)
            try:
                ctypes_binaries = scan_code_for_ctypes(co)
                # As this scan happens after automatic binary-vs-data classification, we need to validate the binaries
                # ourselves, just in case.
                for dest_name, src_name, typecode in set(ctypes_binaries):
                    # Allow for `None` in case re-classification is not supported on the given platform.
                    if bindepend.classify_binary_vs_data(src_name) not in (None, 'BINARY'):
                        logger.warning("Ignoring %s found via ctypes - not a valid binary!", src_name)
                        continue
                    self.binaries.append((dest_name, src_name, typecode))
            except Exception as ex:
                raise RuntimeError(f"Failed to scan the module '{name}'. This is a bug. Please report it.") from ex

        self.datas.extend((dest, source, "DATA")
                          for (dest, source) in format_binaries_and_datas(self.graph.metadata_required()))

        # Analyze run-time hooks. Run-time hooks has to be executed before user scripts. Add them to the beginning of
        # 'priority_scripts'.
        priority_scripts = self.graph.analyze_runtime_hooks(self.custom_runtime_hooks) + priority_scripts

        # 'priority_scripts' is now a list of the graph nodes of custom runtime hooks, then regular runtime hooks, then
        # the PyI loader scripts. Further on, we will make sure they end up at the front of self.scripts

        # -- Extract the nodes of the graph as TOCs for further processing. --

        # Initialize the scripts list with priority scripts in the proper order.
        self.scripts = self.graph.nodes_to_toc(priority_scripts)
        self.scripts = normalize_toc(self.scripts)  # Should not really contain duplicates, but just in case...

        # Extend the binaries list with all the Extensions modulegraph has found.
        self.binaries += self.graph.make_binaries_toc()

        # Convert extension module names into full filenames, and append suffix. Ensure that extensions that come from
        # the lib-dynload are collected into _MEIPASS/lib-dynload instead of directly into _MEIPASS.
        for idx, (dest, source, typecode) in enumerate(self.binaries):
            if typecode != 'EXTENSION':
                continue

            # Convert to full filename and append suffix
            dest, source, typecode = add_suffix_to_extension(dest, source, typecode)

            # Divert into lib-dyload, if necessary (i.e., if file comes from lib-dynload directory) and its destination
            # path does not already have a directory prefix.
            src_parent = os.path.basename(os.path.dirname(source))
            if src_parent == 'lib-dynload' and not os.path.dirname(os.path.normpath(dest)):
                dest = os.path.join('lib-dynload', dest)

            # Update
            self.binaries[idx] = (dest, source, typecode)

        # Perform initial normalization of `datas` and `binaries`
        self.datas = normalize_toc(self.datas)
        self.binaries = normalize_toc(self.binaries)

        # Post-process GLib schemas
        self.datas = compile_glib_schema_files(self.datas, os.path.join(CONF['workpath'], "_pyi_gschema_compilation"))
        self.datas = normalize_toc(self.datas)

        # Process the pure-python modules list. Depending on the collection mode, these entries end up either in "pure"
        # list for collection into the PYZ archive, or in the "datas" list for collection as external data files.
        assert len(self.pure) == 0
        pure_pymodules_toc = self.graph.make_pure_toc()

        # Merge package collection mode settings from .spec file. These are applied last, so they override the
        # settings previously applied by hooks.
        self.graph._module_collection_mode.update(self.module_collection_mode)
        logger.debug("Module collection settings: %r", self.graph._module_collection_mode)

        pycs_dir = os.path.join(CONF['workpath'], 'localpycs')
        code_cache = self.graph.get_code_objects()

        for name, src_path, typecode in pure_pymodules_toc:
            assert typecode == 'PYMODULE'
            collect_mode = _get_module_collection_mode(self.graph._module_collection_mode, name, self.noarchive)

            # Collect byte-compiled .pyc into PYZ archive
            if _ModuleCollectionMode.PYZ in collect_mode:
                self.pure.append((name, src_path, typecode))

            # Pure namespace packages have no source path, and cannot be collected as external data file.
            if src_path in (None, '-'):
                continue

            # Collect source .py file as external data file
            if _ModuleCollectionMode.PY in collect_mode:
                dest_path = name.replace('.', os.sep)
                # Special case: modules have an implied filename to add.
                basename, ext = os.path.splitext(os.path.basename(src_path))
                if basename == '__init__':
                    dest_path += os.sep + '__init__' + ext
                else:
                    dest_path += ext
                self.datas.append((dest_path, src_path, "DATA"))

            # Collect byte-compiled .pyc file as external data file
            if _ModuleCollectionMode.PYC in collect_mode:
                dest_path = name.replace('.', os.sep)
                # Special case: modules have an implied filename to add.
                basename, ext = os.path.splitext(os.path.basename(src_path))
                if basename == '__init__':
                    dest_path += os.sep + '__init__'
                # Append the extension for the compiled result. In python 3.5 (PEP-488) .pyo files were replaced by
                # .opt-1.pyc and .opt-2.pyc. However, it seems that for bytecode-only module distribution, we always
                # need to use the .pyc extension.
                dest_path += '.pyc'

                # Compile
                obj_path = compile_pymodule(name, src_path, workpath=pycs_dir, code_cache=code_cache)

                self.datas.append((dest_path, obj_path, "DATA"))

        # Normalize list of pure-python modules (these will end up in PYZ archive, so use specific normalization).
        self.pure = normalize_pyz_toc(self.pure)

        # Associate the `pure` TOC list instance with code cache in the global `CONF`; this is used by `PYZ` writer
        # to obtain modules' code from cache instead
        #
        # (NOTE: back when `pure` was an instance of `TOC` class, the code object was passed by adding an attribute
        # to the `pure` itself; now that `pure` is plain `list`, we cannot do that anymore. But the association via
        # object ID should have the same semantics as the added attribute).
        from PyInstaller.config import CONF
        global_code_cache_map = CONF['code_cache']
        global_code_cache_map[id(self.pure)] = code_cache

        # Add remaining binary dependencies - analyze Python C-extensions and what DLLs they depend on.
        #
        # Up until this point, we did very best not to import the packages into the main process. However, a package
        # may set up additional library search paths during its import (e.g., by modifying PATH or calling the
        # add_dll_directory() function on Windows, or modifying LD_LIBRARY_PATH on Linux). In order to reliably
        # discover dynamic libraries, we therefore require an environment with all packages imported. We achieve that
        # by gathering list of all collected packages, and spawn an isolated process, in which we first import all
        # the packages from the list, and then perform search for dynamic libraries.
        logger.info('Looking for dynamic libraries')

        collected_packages = self.graph.get_collected_packages()
        self.binaries.extend(find_binary_dependencies(self.binaries, collected_packages))

        # Apply work-around for (potential) binaries collected from `pywin32` package...
        if is_win:
            self.binaries = postprocess_binaries_toc_pywin32(self.binaries)
            # With anaconda, we need additional work-around...
            if is_conda:
                self.binaries = postprocess_binaries_toc_pywin32_anaconda(self.binaries)

        # Final normalization of `datas` and `binaries`:
        #  - normalize both TOCs together (to avoid having duplicates across the lists)
        #  - process the combined normalized TOC for symlinks
        #  - split back into `binaries` (BINARY, EXTENSION) and `datas` (everything else)
        combined_toc = normalize_toc(self.datas + self.binaries)
        combined_toc = toc_process_symbolic_links(combined_toc)

        # On macOS, look for binaries collected from .framework bundles, and collect their Info.plist files.
        if is_darwin:
            combined_toc += osxutils.collect_files_from_framework_bundles(combined_toc)

        self.datas = []
        self.binaries = []
        for entry in combined_toc:
            dest_name, src_name, typecode = entry
            if typecode in {'BINARY', 'EXTENSION'}:
                self.binaries.append(entry)
            else:
                self.datas.append(entry)

        # On macOS, the Finder app seems to litter visited directories with `.DS_Store` files. These cause issues with
        # codesigning when placed in mixed-content directories, where our .app bundle generator cross-links data files
        # from `Resources` to `Frameworks` tree, and the `codesign` utility explicitly forbids a `.DS_Store` file to be
        # a symbolic link.
        # But there is no reason for `.DS_Store` files to be collected in the first place, so filter them out.
        if is_darwin:
            self.datas = [(dest_name, src_name, typecode) for dest_name, src_name, typecode in self.datas
                          if os.path.basename(src_name) != '.DS_Store']

        # Write warnings about missing modules.
        self._write_warnings()
        # Write debug information about the graph
        self._write_graph_debug()

        # On macOS, check the SDK version of the binaries to be collected, and warn when the SDK version is either
        # invalid or too low. Such binaries will likely refuse to be loaded when hardened runtime is enabledm and
        # while we cannot do anything about it, we can at least warn the user about it.
        # See: https://developer.apple.com/forums/thread/132526
        if is_darwin:
            binaries_with_invalid_sdk = []
            for dest_name, src_name, typecode in self.binaries:
                sdk_version = osxutils.get_macos_sdk_version(src_name)
                if sdk_version < (10, 9, 0):
                    binaries_with_invalid_sdk.append((dest_name, src_name, sdk_version))
            if binaries_with_invalid_sdk:
                logger.warning("Found one or more binaries with invalid or incompatible macOS SDK version:")
                for dest_name, src_name, sdk_version in binaries_with_invalid_sdk:
                    logger.warning(" * %r, collected as %r; version: %r", src_name, dest_name, sdk_version)
                logger.warning("These binaries will likely cause issues with code-signing and hardened runtime!")

    def _write_warnings(self):
        """
        Write warnings about missing modules. Get them from the graph and use the graph to figure out who tried to
        import them.
        """
        def dependency_description(name, dep_info):
            if not dep_info or dep_info == 'direct':
                imptype = 0
            else:
                imptype = (dep_info.conditional + 2 * dep_info.function + 4 * dep_info.tryexcept)
            return '%s (%s)' % (name, IMPORT_TYPES[imptype])

        from PyInstaller.config import CONF
        miss_toc = self.graph.make_missing_toc()
        with open(CONF['warnfile'], 'w', encoding='utf-8') as wf:
            wf.write(WARNFILE_HEADER)
            for (n, p, status) in miss_toc:
                importers = self.graph.get_importers(n)
                print(
                    status,
                    'module named',
                    n,
                    '- imported by',
                    ', '.join(dependency_description(name, data) for name, data in importers),
                    file=wf
                )
        logger.info("Warnings written to %s", CONF['warnfile'])

    def _write_graph_debug(self):
        """
        Write a xref (in html) and with `--log-level DEBUG` a dot-drawing of the graph.
        """
        from PyInstaller.config import CONF
        with open(CONF['xref-file'], 'w', encoding='utf-8') as fh:
            self.graph.create_xref(fh)
            logger.info("Graph cross-reference written to %s", CONF['xref-file'])
        if logger.getEffectiveLevel() > logging.DEBUG:
            return
        # The `DOT language's <https://www.graphviz.org/doc/info/lang.html>`_ default character encoding (see the end
        # of the linked page) is UTF-8.
        with open(CONF['dot-file'], 'w', encoding='utf-8') as fh:
            self.graph.graphreport(fh)
            logger.info("Graph drawing written to %s", CONF['dot-file'])

    def exclude_system_libraries(self, list_of_exceptions=None):
        """
        This method may be optionally called from the spec file to exclude any system libraries from the list of
        binaries other than those containing the shell-style wildcards in list_of_exceptions. Those that match
        '*python*' or are stored under 'lib-dynload' are always treated as exceptions and not excluded.
        """

        self.binaries = [
            entry for entry in self.binaries if _should_include_system_binary(entry, list_of_exceptions or [])
        ]


class ExecutableBuilder:
    """
    Class that constructs the executable.
    """
    # TODO wrap the 'main' and 'build' function into this class.


def build(spec, distpath, workpath, clean_build):
    """
    Build the executable according to the created SPEC file.
    """
    from PyInstaller.config import CONF

    # Ensure starting tilde and environment variables get expanded in distpath / workpath.
    # '~/path/abc', '${env_var_name}/path/abc/def'
    distpath = os.path.abspath(compat.expand_path(distpath))
    workpath = os.path.abspath(compat.expand_path(workpath))
    CONF['spec'] = os.path.abspath(compat.expand_path(spec))

    CONF['specpath'], CONF['specnm'] = os.path.split(CONF['spec'])
    CONF['specnm'] = os.path.splitext(CONF['specnm'])[0]

    # Add 'specname' to workpath and distpath if they point to PyInstaller homepath.
    if os.path.dirname(distpath) == HOMEPATH:
        distpath = os.path.join(HOMEPATH, CONF['specnm'], os.path.basename(distpath))
    CONF['distpath'] = distpath
    if os.path.dirname(workpath) == HOMEPATH:
        workpath = os.path.join(HOMEPATH, CONF['specnm'], os.path.basename(workpath), CONF['specnm'])
    else:
        workpath = os.path.join(workpath, CONF['specnm'])
    CONF['workpath'] = workpath

    CONF['warnfile'] = os.path.join(workpath, 'warn-%s.txt' % CONF['specnm'])
    CONF['dot-file'] = os.path.join(workpath, 'graph-%s.dot' % CONF['specnm'])
    CONF['xref-file'] = os.path.join(workpath, 'xref-%s.html' % CONF['specnm'])

    CONF['code_cache'] = dict()

    # Clean PyInstaller cache (CONF['cachedir']) and temporary files (workpath) to be able start a clean build.
    if clean_build:
        logger.info('Removing temporary files and cleaning cache in %s', CONF['cachedir'])
        for pth in (CONF['cachedir'], workpath):
            if os.path.exists(pth):
                # Remove all files in 'pth'.
                for f in glob.glob(pth + '/*'):
                    # Remove dirs recursively.
                    if os.path.isdir(f):
                        shutil.rmtree(f)
                    else:
                        os.remove(f)

    # Create DISTPATH and workpath if they does not exist.
    for pth in (CONF['distpath'], CONF['workpath']):
        os.makedirs(pth, exist_ok=True)

    # Construct NAMESPACE for running the Python code from .SPEC file.
    # NOTE: Passing NAMESPACE allows to avoid having global variables in this module and makes isolated environment for
    #       running tests.
    # NOTE: Defining NAMESPACE allows to map any class to a apecific name for .SPEC.
    # FIXME: Some symbols might be missing. Add them if there are some failures.
    # TODO: What from this .spec API is deprecated and could be removed?
    spec_namespace = {
        # Set of global variables that can be used while processing .spec file. Some of them act as configuration
        # options.
        'DISTPATH': CONF['distpath'],
        'HOMEPATH': HOMEPATH,
        'SPEC': CONF['spec'],
        'specnm': CONF['specnm'],
        'SPECPATH': CONF['specpath'],
        'WARNFILE': CONF['warnfile'],
        'workpath': CONF['workpath'],
        # PyInstaller classes for .spec.
        'TOC': TOC,  # Kept for backward compatibility even though `TOC` class is deprecated.
        'Analysis': Analysis,
        'BUNDLE': BUNDLE,
        'COLLECT': COLLECT,
        'EXE': EXE,
        'MERGE': MERGE,
        'PYZ': PYZ,
        'Tree': Tree,
        'Splash': Splash,
        # Python modules available for .spec.
        'os': os,
    }

    # Execute the specfile. Read it as a binary file...
    try:
        with open(spec, 'rb') as f:
            # ... then let Python determine the encoding, since ``compile`` accepts byte strings.
            code = compile(f.read(), spec, 'exec')
    except FileNotFoundError:
        raise SystemExit(f'Spec file "{spec}" not found!')
    exec(code, spec_namespace)


def __add_options(parser):
    parser.add_argument(
        "--distpath",
        metavar="DIR",
        default=DEFAULT_DISTPATH,
        help="Where to put the bundled app (default: ./dist)",
    )
    parser.add_argument(
        '--workpath',
        default=DEFAULT_WORKPATH,
        help="Where to put all the temporary work files, .log, .pyz and etc. (default: ./build)",
    )
    parser.add_argument(
        '-y',
        '--noconfirm',
        action="store_true",
        default=False,
        help="Replace output directory (default: %s) without asking for confirmation" %
        os.path.join('SPECPATH', 'dist', 'SPECNAME'),
    )
    parser.add_argument(
        '--upx-dir',
        default=None,
        help="Path to UPX utility (default: search the execution path)",
    )
    parser.add_argument(
        '--clean',
        dest='clean_build',
        action='store_true',
        default=False,
        help="Clean PyInstaller cache and remove temporary files before building.",
    )


def main(
    pyi_config,
    specfile,
    noconfirm=False,
    distpath=DEFAULT_DISTPATH,
    workpath=DEFAULT_WORKPATH,
    upx_dir=None,
    clean_build=False,
    **kw
):
    from PyInstaller.config import CONF
    CONF['noconfirm'] = noconfirm

    # If configuration dict is supplied - skip configuration step.
    if pyi_config is None:
        import PyInstaller.configure as configure
        CONF.update(configure.get_config(upx_dir=upx_dir))
    else:
        CONF.update(pyi_config)

    CONF['ui_admin'] = kw.get('ui_admin', False)
    CONF['ui_access'] = kw.get('ui_uiaccess', False)

    build(specfile, distpath, workpath, clean_build)
