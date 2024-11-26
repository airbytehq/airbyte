# ----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

import glob
import os
import pathlib

from PyInstaller import compat
from PyInstaller import isolated
from PyInstaller import log as logging
from PyInstaller.depend import bindepend
from PyInstaller.utils import hooks, misc
from PyInstaller.utils.hooks.qt import _modules_info

logger = logging.getLogger(__name__)

# Qt deployment approach
# ----------------------
# This is the core of PyInstaller's approach to Qt deployment. It is based on:
#
# - Discovering the location of Qt libraries by introspection, using QtLibraryInfo_. This provides compatibility with
#   many variants of Qt5/6 (conda, self-compiled, provided by a Linux distro, etc.) and many versions of Qt5/6, all of
#   which vary in the location of Qt files.
#
# - Placing all frozen PyQt5/6 or PySide2/6 Qt files in a standard subdirectory layout, which matches the layout of the
#   corresponding wheel on PyPI. This is necessary to support Qt installs which are not in a subdirectory of the PyQt5/6
#   or PySide2/6 wrappers. See ``hooks/rthooks/pyi_rth_qt5.py`` for the use of environment variables to establish this
#   layout.
#
# - Emitting warnings on missing QML and translation files which some installations do not have.
#
# - Determining additional files needed for deployment based on the information in the centralized Qt module information
#   list in the ``_modules_info`` module. This includes plugins and translation files associated with each Qt python
#   extension module, as well as additional python Qt extension modules.
#
# - Collecting additional files that are specific to each module and are handled separately, for example:
#
#    - For dynamic OpenGL applications, the ``libEGL.dll``, ``libGLESv2.dll``, ``d3dcompiler_XX.dll`` (the XX is a
#      version number), and ``opengl32sw.dll`` libraries need to be collected on Windows. This is handled by the
#      "base" bindings hook, for example ``hook-PyQt5.py``.
#
#    - If Qt was configured to use ICU, the ``icudtXX.dll``, ``icuinXX.dll``, and ``icuucXX.dll`` libraries need to
#      be collected on Windows. This is handled by the "base" bindings hook, for example ``hook-PyQt5.py``.
#
#    - Per the `Deploying QML Applications <http://doc.qt.io/qt-5/qtquick-deployment.html>`_ page, QML-based
#      applications need the ``qml/`` directory available. This is handled by ``QtQuick`` hook, for example
#      ``hook-PyQt5.QtQuick.py``.
#
#    - For ``QtWebEngine``-based applications, we follow the `deployWebEngineCore
#      <https://code.woboq.org/qt5/qttools/src/windeployqt/main.cpp.html#_ZL19deployWebEngineCoreRK4QMapI7QStringS0_ERK7OptionsbPS0_>`_
#      function copies the following files from ``resources/``, and also copies the web engine process executable.
#       -   ``icudtl.dat``
#       -   ``qtwebengine_devtools_resources.pak``
#       -   ``qtwebengine_resources.pak``
#       -   ``qtwebengine_resources_100p.pak``
#       -   ``qtwebengine_resources_200p.pak``
#
#      This is handled by the ``QtWebEngineCore`` hook, for example  ``hook-PyQt5.QtWebEngineCore.py``.
#
# For details and references, see the `original write-up
# <https://github.com/pyinstaller/pyinstaller/blob/fbf7948be85177dd44b41217e9f039e1d176de6b/PyInstaller/utils/hooks/qt.py#L248-L362>`_
# and the documentation in the ``_modules_info`` module.


# QtModuleInfo
# ------------
# This class contains information about python module (extension), its corresponding Qt module (shared library), and
# associated plugins and translations. It is used within QtLibraryInfo_ to establish name-based mappings for file
# collection.
class QtModuleInfo:
    def __init__(self, module, shared_lib=None, translations=None, plugins=None):
        # Python module (extension) name without package namespace. For example, `QtCore`.
        # Can be None if python bindings do not bind the module, but we still need to establish relationship between
        # the Qt module (shared library) and its plugins and translations.
        self.module = module
        # Associated Qt module (shared library), if any. Used during recursive dependency analysis, where a python
        # module (extension) is analyzed for linked Qt modules (shared libraries), and then their corresponding
        # python modules (extensions) are added to hidden imports. For example, the Qt module name is `Qt5Core` or
        # `Qt6Core`, depending on the Qt version. Can be None for python modules that are not tied to a particular
        # Qt shared library (for example, the corresponding Qt module is headers-only) and hence they cannot be
        # inferred from recursive link-time dependency analysis.
        self.shared_lib = shared_lib
        # List of base names of translation files (if any) associated with the Qt module. Multiple base names may be
        # associated with a single module.
        # For example, `['qt', 'qtbase']` for `QtCore` or `['qtmultimedia']` for `QtMultimedia`.
        self.translations = translations or []
        # List of plugins associated with the Qt module.
        self.plugins = plugins or []

    def __repr__(self):
        return f"(module={self.module!r}, shared_lib={self.shared_lib!r}, " \
               f"translations={self.translations!r}, plugins={self.plugins!r}"


# QtLibraryInfo
# --------------
# This class uses introspection to determine the location of Qt files. This is essential to deal with the many variants
# of the PyQt5/6 and PySide2/6 package, each of which places files in a different location. Therefore, this class
# provides all location-related members of `QLibraryInfo <http://doc.qt.io/qt-5/qlibraryinfo.html>`_.
class QtLibraryInfo:
    def __init__(self, namespace):
        if namespace not in ['PyQt5', 'PyQt6', 'PySide2', 'PySide6']:
            raise Exception('Invalid namespace: {0}'.format(namespace))
        self.namespace = namespace
        # Distinction between PyQt5/6 and PySide2/6
        self.is_pyqt = namespace in {'PyQt5', 'PyQt6'}
        # Distinction between Qt5 and Qt6
        self.qt_major = 6 if namespace in {'PyQt6', 'PySide6'} else 5
        # Determine relative path where Qt libraries and data need to be collected in the frozen application. This
        # varies between PyQt5/PyQt6/PySide2/PySide6, their versions, and platforms. NOTE: it is tempting to consider
        # deriving this path as simply the value of QLibraryInfo.PrefixPath, taken relative to the package's root
        # directory. However, we also need to support non-wheel deployments (e.g., with Qt installed in custom path on
        # Windows, or with Qt and PyQt5 installed on linux using native package manager), and in those, the Qt
        # PrefixPath does not reflect the required relative target path for the frozen application.
        if namespace == 'PyQt5':
            if self._use_new_layout("PyQt5", "5.15.4", False):
                self.qt_rel_dir = os.path.join('PyQt5', 'Qt5')
            else:
                self.qt_rel_dir = os.path.join('PyQt5', 'Qt')
        elif namespace == 'PyQt6':
            if self._use_new_layout("PyQt6", "6.0.3", True):
                self.qt_rel_dir = os.path.join('PyQt6', 'Qt6')
            else:
                self.qt_rel_dir = os.path.join('PyQt6', 'Qt')
        elif namespace == 'PySide2':
            # PySide2 uses PySide2/Qt on linux and macOS, and PySide2 on Windows
            if compat.is_win:
                self.qt_rel_dir = 'PySide2'
            else:
                self.qt_rel_dir = os.path.join('PySide2', 'Qt')
        else:
            # PySide6 follows the same logic as PySide2
            if compat.is_win:
                self.qt_rel_dir = 'PySide6'
            else:
                self.qt_rel_dir = os.path.join('PySide6', 'Qt')

        # Process module information list to construct python-module-name -> info and shared-lib-name -> info mappings.
        self._load_module_info()

    def __repr__(self):
        return f"QtLibraryInfo({self.namespace})"

    # Delay initialization of the Qt library information until the corresponding attributes are first requested.
    def __getattr__(self, name):
        if 'version' in self.__dict__:
            # Initialization was already done, but requested attribute is not available.
            raise AttributeError(name)

        # Load Qt library info...
        self._load_qt_info()
        # ... and return the requested attribute
        return getattr(self, name)

    # Check whether we must use the new layout (e.g. PyQt5/Qt5, PyQt6/Qt6) instead of the old layout (PyQt5/Qt,
    # PyQt6/Qt).
    @staticmethod
    def _use_new_layout(package_basename: str, version: str, fallback_value: bool) -> bool:
        # The PyQt wheels come in both non-commercial and commercial variants. So we need to check if a particular
        # variant is installed before testing its version.
        if hooks.check_requirement(package_basename):
            return hooks.check_requirement(f"{package_basename} >= {version}")
        if hooks.check_requirement(f"{package_basename}_commercial"):
            return hooks.check_requirement(f"{package_basename}_commercial >= {version}")
        return fallback_value

    # Load Qt information (called on first access to related fields)
    def _load_qt_info(self):
        """
        Load and process Qt library information. Called on the first access to the related attributes of the class
        (e.g., `version` or `location`).
        """

        # Ensure self.version exists, even if PyQt{5,6}/PySide{2,6} cannot be imported. Hooks and util functions use
        # `if .version` to check whether package was imported and other attributes are expected to be available.
        # This also serves as a marker that initialization was already done.
        self.version = None

        # Get library path information from Qt. See QLibraryInfo_.
        @isolated.decorate
        def _read_qt_library_info(package):
            import os
            import sys
            import importlib

            # Import the Qt-based package
            # equivalent to: from package.QtCore import QLibraryInfo, QCoreApplication
            QtCore = importlib.import_module('.QtCore', package)
            QLibraryInfo = QtCore.QLibraryInfo
            QCoreApplication = QtCore.QCoreApplication

            # QLibraryInfo is not always valid until a QCoreApplication is instantiated.
            app = QCoreApplication(sys.argv)  # noqa: F841

            # Qt6 deprecated QLibraryInfo.location() in favor of QLibraryInfo.path(), and
            # QLibraryInfo.LibraryLocation enum was replaced by QLibraryInfo.LibraryPath.
            if hasattr(QLibraryInfo, 'path'):
                # Qt6; enumerate path enum values directly from the QLibraryInfo.LibraryPath enum.
                path_names = [x for x in dir(QLibraryInfo.LibraryPath) if x.endswith('Path')]
                location = {x: QLibraryInfo.path(getattr(QLibraryInfo.LibraryPath, x)) for x in path_names}
            else:
                # Qt5; in recent versions, location enum values can be enumeratd from QLibraryInfo.LibraryLocation.
                # However, in older versions of Qt5 and its python bindings, that is unavailable. Hence the
                # enumeration of "*Path"-named members of QLibraryInfo.
                path_names = [x for x in dir(QLibraryInfo) if x.endswith('Path')]
                location = {x: QLibraryInfo.location(getattr(QLibraryInfo, x)) for x in path_names}

            # Determine the python-based package location, by looking where the QtCore module is located.
            package_location = os.path.dirname(QtCore.__file__)

            # Determine Qt version. Works for Qt 5.8 and later, where QLibraryInfo.version() was introduced.
            try:
                version = QLibraryInfo.version().segments()
            except AttributeError:
                version = []

            return {
                'is_debug_build': QLibraryInfo.isDebugBuild(),
                'version': version,
                'location': location,
                'package_location': package_location,
            }

        try:
            qt_info = _read_qt_library_info(self.namespace)
        except Exception as e:
            logger.warning("%s: failed to obtain Qt library info: %s", self, e)
            qt_info = {}

        for k, v in qt_info.items():
            setattr(self, k, v)

    # Module information list loading/processing
    def _load_module_info(self):
        """
        Process the Qt modules info definition list and construct two dictionaries:
         - dictionary that maps Qt python module names to Qt module info entries
         - dictionary that maps shared library names to Qt module info entries
        """

        self.python_modules = dict()
        self.shared_libraries = dict()

        for entry in _modules_info.QT_MODULES_INFO:
            # If entry specifies applicable bindings, check them
            if entry.bindings:
                applicable_bindings = _modules_info.process_namespace_strings(entry.bindings)
                if self.namespace not in applicable_bindings:
                    continue

            # Create a QtModuleInfo entry
            info_entry = QtModuleInfo(
                module=entry.module,
                shared_lib=f"Qt{self.qt_major}{entry.shared_lib}" if entry.shared_lib else None,
                translations=entry.translations,
                plugins=entry.plugins
            )

            # If we have python module (extension) name, create python-module-name -> info mapping.
            if info_entry.module is not None:
                self.python_modules[info_entry.module] = info_entry

            # If we have Qt module (shared library) name, create shared-lib-name -> info mapping.
            if info_entry.shared_lib is not None:
                self.shared_libraries[info_entry.shared_lib.lower()] = info_entry

    # Collection
    def collect_module(self, module_name):
        """
        Collect all dependencies (hiddenimports, binaries, datas) for the given Qt python module.

        This function performs recursive analysis of extension module's link-time dependencies, and uses dictionaries
        built by `_load_module_info` to discover associated plugin types, translation file base names, and hidden
        imports that need to be collected.
        """

        # Accumulate all dependencies in a set to avoid duplicates.
        hiddenimports = set()
        translation_base_names = set()
        plugin_types = set()

        # Exit if the requested library cannot be imported.
        # NOTE: self..version can be empty list on older Qt5 versions (#5381).
        if self.version is None:
            return [], [], []

        logger.debug('%s: processing module %s...', self, module_name)

        # Look up the associated Qt module information by python module name.
        # This allows us to collect associated module data directly, even if there is no associated shared library
        # (e.g., header-only Qt module, or statically-built one).
        short_module_name = module_name.split('.', 1)[-1]  # PySide2.QtModule -> QtModule
        if short_module_name in self.python_modules:
            qt_module_info = self.python_modules[short_module_name]

            # NOTE: no need to add a hiddenimport here, because this is the module under consideration.

            # Add plugins
            plugin_types.update(qt_module_info.plugins)

            # Add translation base name(s)
            translation_base_names.update(qt_module_info.translations)

        # Find the actual module extension file.
        module_file = hooks.get_module_file_attribute(module_name)

        # Additional search path for shared library resolution. This is mostly required for library resolution on
        # Windows (Linux and macOS binaries use run paths to find Qt libs).
        qtlib_search_paths = [
            # For PyQt5 and PyQt6 wheels, shared libraries should be in BinariesPath, while for PySide2 and PySide6,
            # they should be in PrefixPath.
            self.location['BinariesPath' if self.is_pyqt else 'PrefixPath'],
        ]

        # Walk through all the link-time dependencies of a dynamically-linked library (``.so``/``.dll``/``.dylib``).
        imported_libraries = bindepend.get_imports(module_file, qtlib_search_paths)
        while imported_libraries:
            imported_lib_name, imported_lib_path = imported_libraries.pop()  # (name, fullpath) tuple

            # Skip unresolved libraries
            if imported_lib_path is None:
                logger.debug("%s: ignoring unresolved library import %r", self, imported_lib_name)
                continue

            # On macOS, ``imported_lib_name`` is the original referenced name and may not be a basename. So, to parse
            # the library name, obtain the base name of the full library path (``imported_lib_path``). Remove the
            # suffix and "lib" prefix (Linux/macOS), and lowercase the name for case-normalized comparison.
            lib_name = os.path.splitext(os.path.basename(imported_lib_path))[0].lower()
            # Linux libraries sometimes have a dotted version number -- ``libfoo.so.3``. It is now ''libfoo.so``,
            # but the ``.so`` must also be removed.
            if compat.is_linux and os.path.splitext(lib_name)[1] == '.so':
                lib_name = os.path.splitext(lib_name)[0]
            if lib_name.startswith('lib'):
                lib_name = lib_name[3:]
            # macOS: handle different naming schemes. PyPI wheels ship framework-enabled Qt builds, where shared
            # libraries are part of .framework bundles (e.g., ``PyQt5/Qt5/lib/QtCore.framework/Versions/5/QtCore``).
            # In Anaconda (Py)Qt installations, the shared libraries are installed in environment's library directory,
            # and contain versioned extensions, e.g., ``libQt5Core.5.dylib``.
            if compat.is_darwin:
                if lib_name.startswith('qt') and not lib_name.startswith('qt' + str(self.qt_major)):
                    # Qt library from a framework bundle (e.g., ``QtCore``); change prefix from ``qt`` to ``qt5`` or
                    # ``qt6`` to match names in Windows/Linux.
                    lib_name = 'qt' + str(self.qt_major) + lib_name[2:]
                if lib_name.endswith('.' + str(self.qt_major)):
                    # Qt library from Anaconda, which originally had versioned extension, e.g., ``libfoo.5.dynlib``.
                    # The above processing turned it into ``foo.5``, so we need to remove the last two characters.
                    lib_name = lib_name[:-2]

            # Match libs with QT_LIBINFIX set to '_conda', i.e. conda-forge builds.
            if lib_name.endswith('_conda'):
                lib_name = lib_name[:-6]

            logger.debug(
                '%s: imported library %r, full path %r -> parsed name %r.', self, imported_lib_name, imported_lib_path,
                lib_name
            )

            # PySide2 and PySide6 on linux seem to link all extension modules against libQt5Core, libQt5Network, and
            # libQt5Qml (or their libQt6* equivalents). While the first two are reasonable, the libQt5Qml dependency
            # pulls in whole QtQml module, along with its data and plugins, which in turn pull in several other Qt
            # libraries, greatly inflating the bundle size (see #6447).
            #
            # Similarly, some extension modules (QtWebChannel, QtWebEngine*) seem to be also linked against libQt5Qml,
            # even when the module can be used without having the whole QtQml module collected.
            #
            # Therefore, we explicitly prevent inclusion of QtQml based on the dynamic library dependency, except for
            # QtQml* and QtQuick* modules, whose use directly implies the use of QtQml.
            if lib_name in ("qt5qml", "qt6qml"):
                if not short_module_name.startswith(('QtQml', 'QtQuick')):
                    logger.debug('%s: ignoring imported library %r.', self, lib_name)
                    continue

            # Use the parsed library name to look up associated Qt module information.
            if lib_name in self.shared_libraries:
                logger.debug('%s: collecting Qt module associated with %r.', self, lib_name)

                # Look up associated module info
                qt_module_info = self.shared_libraries[lib_name]

                # If there is a python extension module associated with Qt module, add it to hiddenimports. Since this
                # means that we (most likely) have a hook available for that module, we can avoid analyzing the shared
                # library itself (i.e., stop the recursive analysis), because this will be done by the corresponding
                # hook.
                if qt_module_info.module:
                    if qt_module_info.module == short_module_name:
                        # The one exception is if we are analyzing shared library associated with the input module; in
                        # that case, avoid adding a hidden import and analyze the library's link-time dependencies. We
                        # do not need to worry about plugins and translations for this particular module, because those
                        # have been handled at the beginning of this function.
                        imported_libraries.update(bindepend.get_imports(imported_lib_path, qtlib_search_paths))
                    else:
                        hiddenimports.add(self.namespace + "." + qt_module_info.module)
                    continue

                # Add plugins
                plugin_types.update(qt_module_info.plugins)

                # Add translation base name(s)
                translation_base_names.update(qt_module_info.translations)

                # Analyze the linked shared libraries for its dependencies (recursive analysis).
                imported_libraries.update(bindepend.get_imports(imported_lib_path, qtlib_search_paths))

        # Collect plugin files.
        binaries = []
        for plugin_type in plugin_types:
            binaries += self.collect_plugins(plugin_type)

        # Collect translation files.
        datas = []
        translation_src = self.location['TranslationsPath']
        translation_dst = os.path.join(self.qt_rel_dir, 'translations')

        for translation_base_name in translation_base_names:
            # Not all PyQt5 installations include translations. See
            # https://github.com/pyinstaller/pyinstaller/pull/3229#issuecomment-359479893
            # and
            # https://github.com/pyinstaller/pyinstaller/issues/2857#issuecomment-368744341.
            translation_pattern = os.path.join(translation_src, translation_base_name + '_*.qm')
            translation_files = glob.glob(translation_pattern)
            if translation_files:
                datas += [(translation_file, translation_dst) for translation_file in translation_files]
            else:
                logger.warning(
                    '%s: could not find translations with base name %r! These translations will not be collected.',
                    self, translation_base_name
                )

        # Convert hiddenimports to a list.
        hiddenimports = list(hiddenimports)

        logger.debug(
            '%s: dependencies for %s:\n'
            '  hiddenimports = %r\n'
            '  binaries = %r\n'
            '  datas = %r', self, module_name, hiddenimports, binaries, datas
        )

        return hiddenimports, binaries, datas

    @staticmethod
    def _filter_release_plugins(plugin_files):
        """
        Filter the provided list of Qt plugin files and remove the debug variants, under the assumption that both the
        release version of a plugin (qtplugin.dll) and its debug variant (qtplugind.dll) appear in the list.
        """
        # All basenames for lookup
        plugin_basenames = {os.path.normcase(os.path.basename(f)) for f in plugin_files}
        # Process all given filenames
        release_plugin_files = []
        for plugin_filename in plugin_files:
            plugin_basename = os.path.normcase(os.path.basename(plugin_filename))
            if plugin_basename.endswith('d.dll'):
                # If we can find a variant without trailing 'd' in the plugin list, then the DLL we are dealing with is
                # a debug variant and needs to be excluded.
                release_name = os.path.splitext(plugin_basename)[0][:-1] + '.dll'
                if release_name in plugin_basenames:
                    continue
            release_plugin_files.append(plugin_filename)
        return release_plugin_files

    def collect_plugins(self, plugin_type):
        """
        Collect all plugins of the specified type from the Qt plugin directory.

        Returns list of (src, dst) tuples.
        """
        # Ensure plugin directory exists
        plugin_src_dir = self.location['PluginsPath']
        if not os.path.isdir(plugin_src_dir):
            raise Exception(f"Qt plugin directory '{plugin_src_dir}' does not exist!")

        # Collect all shared lib files in plugin type (sub)directory
        plugin_files = misc.dlls_in_dir(os.path.join(plugin_src_dir, plugin_type))

        # Windows:
        #
        # dlls_in_dir() grabs all files ending with ``*.dll``, ``*.so`` and ``*.dylib`` in a certain directory. On
        # Windows this would grab debug copies of Qt plugins, which then causes PyInstaller to add a dependency on the
        # Debug CRT *in addition* to the release CRT.
        if compat.is_win:
            plugin_files = self._filter_release_plugins(plugin_files)

        logger.debug("%s: found plugin files for plugin type %r: %r", self, plugin_type, plugin_files)

        plugin_dst_dir = os.path.join(self.qt_rel_dir, 'plugins', plugin_type)
        return [(plugin_file, plugin_dst_dir) for plugin_file in plugin_files]

    def _collect_all_or_none(self, mandatory_dll_patterns, optional_dll_patterns=None):
        """
        Try to find Qt DLLs from the specified mandatory pattern list. If all mandatory patterns resolve to DLLs,
        collect them all, as well as any DLLs from the optional pattern list. If a mandatory pattern fails to resolve
        to a DLL, return an empty list.

        This allows all-or-none collection of particular groups of Qt DLLs that may or may not be available.
        """
        optional_dll_patterns = optional_dll_patterns or []

        # Resolve path to the the corresponding python package (actually, its parent directory). Used to preserve the
        # directory structure when DLLs are collected from the python package (e.g., PyPI wheels).
        package_parent_path = pathlib.Path(self.package_location).resolve().parent

        # In PyQt5 and PyQt6, the DLLs we are looking for are located in location['BinariesPath'], whereas in PySide2
        # and PySide6, they are located in location['PrefixPath'].
        dll_path = self.location['BinariesPath' if self.is_pyqt else 'PrefixPath']
        dll_path = pathlib.Path(dll_path).resolve()

        # Helper for processing single DLL pattern
        def _process_dll_pattern(dll_pattern):
            discovered_dlls = []

            dll_files = dll_path.glob(dll_pattern)
            for dll_file in dll_files:
                if package_parent_path in dll_file.parents:
                    # The DLL is located within python package; preserve the layout
                    dst_dll_dir = dll_file.parent.relative_to(package_parent_path)
                else:
                    # The DLL is not located within python package; collect into top-level directory
                    dst_dll_dir = '.'
                discovered_dlls.append((str(dll_file), str(dst_dll_dir)))

            return discovered_dlls

        # Process mandatory patterns
        collected_dlls = []
        for pattern in mandatory_dll_patterns:
            discovered_dlls = _process_dll_pattern(pattern)
            if not discovered_dlls:
                return []  # Mandatory pattern resulted in no DLLs; abort
            collected_dlls += discovered_dlls

        # Process optional patterns
        for pattern in optional_dll_patterns:
            collected_dlls += _process_dll_pattern(pattern)

        return collected_dlls

    # Collect required Qt binaries, but only if all binaries in a group exist.
    def collect_extra_binaries(self):
        """
        Collect extra binaries/DLLs required by Qt. These include ANGLE DLLs, OpenGL software renderer DLL, and ICU
        DLLs. Applicable only on Windows (on other OSes, empty list is returned).
        """

        binaries = []

        # Applicable only to Windows.
        if not compat.is_win:
            return []

        # OpenGL: EGL/GLES via ANGLE, software OpenGL renderer.
        binaries += self._collect_all_or_none(['libEGL.dll', 'libGLESv2.dll'], ['d3dcompiler_??.dll'])
        binaries += self._collect_all_or_none(['opengl32sw.dll'])

        # Include ICU files, if they exist.
        # See the "Deployment approach" section in ``PyInstaller/utils/hooks/qt.py``.
        binaries += self._collect_all_or_none(['icudt??.dll', 'icuin??.dll', 'icuuc??.dll'])

        return binaries

    # Collect additional shared libraries required for SSL support in QtNetwork, if they are available.
    # Applicable only to Windows. See issue #3520, #4048.
    def collect_qtnetwork_files(self):
        """
        Collect extra binaries/DLLs required by the QtNetwork module. These include OpenSSL DLLs. Applicable only
        on Windows (on other OSes, empty list is returned).
        """

        # No-op if requested Qt-based package is not available.
        if self.version is None:
            return []

        # Applicable only to Windows.
        if not compat.is_win:
            return []

        # Check if QtNetwork supports SSL
        @isolated.decorate
        def _ssl_enabled(package):
            import sys
            import importlib

            # Import the Qt-based package
            # equivalent to: from package.QtCore import QCoreApplication
            QtCore = importlib.import_module('.QtCore', package)
            QCoreApplication = QtCore.QCoreApplication
            # equivalent to: from package.QtNetwork import QSslSocket
            QtNetwork = importlib.import_module('.QtNetwork', package)
            QSslSocket = QtNetwork.QSslSocket

            # Instantiate QCoreApplication to suppress warnings
            app = QCoreApplication(sys.argv)  # noqa: F841

            return QSslSocket.supportsSsl()

        if not _ssl_enabled(self.namespace):
            return []

        # Resolve path to the the corresponding python package (actually, its parent directory). Used to preserve the
        # directory structure when DLLs are collected from the python package (e.g., PyPI wheels).
        package_parent_path = pathlib.Path(self.package_location).resolve().parent

        # PyPI version of PySide2 requires user to manually install SSL libraries into the PrefixPath. Other versions
        # (e.g., the one provided by Conda) put the libraries into the BinariesPath. PyQt5 also uses BinariesPath.
        # Accommodate both options by searching both locations...
        locations = (self.location['BinariesPath'], self.location['PrefixPath'])
        dll_names = ('libeay32.dll', 'ssleay32.dll', 'libssl-1_1-x64.dll', 'libcrypto-1_1-x64.dll')
        binaries = []
        for location in locations:
            location = pathlib.Path(location).resolve()
            for dll in dll_names:
                dll_file_path = location / dll
                if not dll_file_path.exists():
                    continue
                if package_parent_path in dll_file_path.parents:
                    # The DLL is located within python package; preserve the layout
                    dst_dll_path = dll_file_path.parent.relative_to(package_parent_path)
                else:
                    # The DLL is not located within python package; collect into top-level directory
                    dst_dll_path = '.'
                binaries.append((str(dll_file_path), str(dst_dll_path)))
        return binaries

    def collect_qtqml_files(self):
        """
        Collect additional binaries and data for QtQml module.
        """

        # No-op if requested Qt-based package is not available.
        if self.version is None:
            return [], []

        # Not all PyQt5/PySide2 installs have QML files. In this case, location['Qml2ImportsPath'] is empty.
        # Furthermore, even if location path is provided, the directory itself may not exist.
        #
        # https://github.com/pyinstaller/pyinstaller/pull/3229#issuecomment-359735031
        # https://github.com/pyinstaller/pyinstaller/issues/3864
        #
        # In Qt 6, Qml2ImportsPath was deprecated in favor of QmlImportsPath. The former is not available in PySide6
        # 6.4.0 anymore (but is in PyQt6 6.4.0). Use the new QmlImportsPath if available.
        if 'QmlImportsPath' in self.location:
            qml_src_dir = self.location['QmlImportsPath']
        else:
            qml_src_dir = self.location['Qml2ImportsPath']
        if not qml_src_dir or not os.path.isdir(qml_src_dir):
            logger.warning('%s: QML directory %r does not exist. QML files not packaged.', self, qml_src_dir)
            return [], []

        qml_dst_dir = os.path.join(self.qt_rel_dir, 'qml')
        datas = [(qml_src_dir, qml_dst_dir)]
        binaries = [
            # Produce ``/path/to/Qt/Qml/path_to_qml_binary/qml_binary, PyQt5/Qt/Qml/path_to_qml_binary``.
            (
                qml_plugin_file,
                os.path.join(qml_dst_dir, os.path.dirname(os.path.relpath(qml_plugin_file, qml_src_dir)))
            ) for qml_plugin_file in misc.dlls_in_subdirs(qml_src_dir)
        ]

        return binaries, datas

    def collect_qtwebengine_files(self):
        """
        Collect QtWebEngine helper process executable, translations, and resources.
        """

        binaries = []
        datas = []

        # Output directory (varies between PyQt and PySide and among OSes; the difference is abstracted by
        # QtLibraryInfo.qt_rel_dir)
        rel_data_path = self.qt_rel_dir

        is_macos_framework = False
        if compat.is_darwin:
            # Determine if we are dealing with a framework-based Qt build (e.g., PyPI wheels) or a dylib-based one
            # (e.g., Anaconda). The former requires special handling, while the latter is handled in the same way as
            # Windows and Linux builds.
            is_macos_framework = os.path.exists(
                os.path.join(self.location['LibrariesPath'], 'QtWebEngineCore.framework')
            )

        if is_macos_framework:
            # macOS .framework bundle
            src_framework_path = os.path.join(self.location['LibrariesPath'], 'QtWebEngineCore.framework')

            # If Qt libraries are bundled with the package, collect the .framework bundle into corresponding package's
            # subdirectory, because binary dependency analysis will also try to preserve the directory structure.
            # However, if we are collecting from system-wide Qt installation (e.g., Homebrew-installed Qt), the binary
            # depndency analysis will attempt to re-create .framework bundle in top-level directory, so we need to
            # collect the extra files there.
            bundled_qt_libs = pathlib.Path(self.package_location) in pathlib.Path(src_framework_path).parents
            if bundled_qt_libs:
                dst_framework_path = os.path.join(rel_data_path, 'lib/QtWebEngineCore.framework')
            else:
                dst_framework_path = 'QtWebEngineCore.framework'  # In top-level directory

            # Determine the version directory - for now, we assume we are dealing with single-version framework;
            # i.e., the Versions directory contains only a single <version> directory, and Current symlink to it.
            versions = sorted([
                version for version in os.listdir(os.path.join(src_framework_path, 'Versions')) if version != 'Current'
            ])
            if len(versions) == 0:
                raise RuntimeError("Could not determine version of the QtWebEngineCore.framework!")
            elif len(versions) > 1:
                logger.warning(
                    "Found multiple versions in QtWebEngineCore.framework (%r) - using the last one!", versions
                )
            version = versions[-1]

            # Collect the Helpers directory. In well-formed .framework bundles (such as the ones provided by Homebrew),
            # the Helpers directory is located in the versioned directory, and symlinked to the top-level directory.
            src_helpers_path = os.path.join(src_framework_path, 'Versions', version, 'Helpers')
            dst_helpers_path = os.path.join(dst_framework_path, 'Versions', version, 'Helpers')
            if not os.path.exists(src_helpers_path):
                # Alas, the .framework bundles shipped with contemporary PyPI PyQt/PySide wheels are not well-formed
                # (presumably because .whl cannot preserve symlinks?). The Helpers in the top-level directory is in fact
                # the hard copy, and there is either no Helpers in versioned directory, or there is a duplicate.
                # So fall back to collecting from the top-level, but collect into versioned directory in order to
                # be compliant with codesign's expectations.
                src_helpers_path = os.path.join(src_framework_path, 'Helpers')

            helper_datas = hooks.collect_system_data_files(src_helpers_path, dst_helpers_path)

            # Filter out the actual helper executable from datas, and add it to binaries instead. This ensures that it
            # undergoes additional binary processing that rewrites the paths to linked libraries.
            HELPER_EXE = 'QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess'
            for src_name, dest_name in helper_datas:
                if src_name.endswith(HELPER_EXE):
                    binaries.append((src_name, dest_name))
                else:
                    datas.append((src_name, dest_name))

            # Collect the Resources directory; same logic is used as with Helpers directory.
            src_resources_path = os.path.join(src_framework_path, 'Versions', version, 'Resources')
            dst_resources_path = os.path.join(dst_framework_path, 'Versions', version, 'Resources')
            if not os.path.exists(src_resources_path):
                src_resources_path = os.path.join(src_framework_path, 'Resources')

            datas += hooks.collect_system_data_files(src_resources_path, dst_resources_path)

            # NOTE: the QtWebEngineProcess helper is actually sought within the `QtWebEngineCore.framework/Helpers`,
            # which ought to be a symlink to `QtWebEngineCore.framework/Versions/Current/Helpers`, where `Current`
            # is also a symlink to the actual version directory, `A`.
            #
            # These symlinks are created automatically when the TOC list of collected resources is post-processed
            # using `PyInstaller.utils.osx.collect_files_from_framework_bundles` helper, so we do not have to
            # worry about them here...
        else:
            # Windows and linux (or Anaconda on macOS)
            locales = 'qtwebengine_locales'
            resources = 'resources'

            # Translations
            datas.append((
                os.path.join(self.location['TranslationsPath'], locales),
                os.path.join(rel_data_path, 'translations', locales),
            ))

            # Resources; ``DataPath`` is the base directory for ``resources``, as per the
            # `docs <https://doc.qt.io/qt-5.10/qtwebengine-deploying.html#deploying-resources>`_.
            datas.append((os.path.join(self.location['DataPath'], resources), os.path.join(rel_data_path, resources)),)

            # Helper process executable (QtWebEngineProcess), located in ``LibraryExecutablesPath``.
            dest = os.path.join(
                rel_data_path, os.path.relpath(self.location['LibraryExecutablesPath'], self.location['PrefixPath'])
            )
            binaries.append((os.path.join(self.location['LibraryExecutablesPath'], 'QtWebEngineProcess*'), dest))

            # The helper QtWebEngineProcess executable should have an accompanying qt.conf file that helps it locate the
            # Qt shared libraries. Try collecting it as well
            qt_conf_file = os.path.join(self.location['LibraryExecutablesPath'], 'qt.conf')
            if not os.path.isfile(qt_conf_file):
                # The file seems to have been dropped from Qt 6.3 (and corresponding PySide6 and PyQt6) due to
                # redundancy; however, we still need it in the frozen application - so generate our own.
                from PyInstaller.config import CONF  # workpath
                # Relative path to root prefix of bundled Qt
                rel_prefix = os.path.relpath(self.location['PrefixPath'], self.location['LibraryExecutablesPath'])
                # We expect the relative path to be either . or .. depending on PySide/PyQt layout; if that is not the
                # case, warn about irregular path.
                if rel_prefix not in ('.', '..'):
                    logger.warning(
                        "%s: unexpected relative Qt prefix path for QtWebEngineProcess qt.conf: %s", self, rel_prefix
                    )
                # The Qt docs on qt.conf (https://doc.qt.io/qt-5/qt-conf.html) recommend using forward slashes on
                # Windows as well, due to backslash having to be escaped. This should not matter as we expect the
                # relative path to be . or .., but you never know...
                if os.sep == '\\':
                    rel_prefix = rel_prefix.replace(os.sep, '/')
                # Create temporary file in workpath
                qt_conf_file = os.path.join(CONF['workpath'], "qt.conf")
                with open(qt_conf_file, 'w', encoding='utf-8') as fp:
                    print("[Paths]", file=fp)
                    print("Prefix = {}".format(rel_prefix), file=fp)
            datas.append((qt_conf_file, dest))

        # Add Linux-specific libraries.
        if compat.is_linux:
            # The automatic library detection fails for `NSS <https://packages.ubuntu.com/search?keywords=libnss3>`_,
            # which is used by QtWebEngine. In some distributions, the ``libnss`` supporting libraries are stored in a
            # subdirectory ``nss``. Since ``libnss`` is not linked against them but loads them dynamically at run-time,
            # we need to search for and add them.

            # First, get all libraries linked to ``QtWebEngineCore`` extension module.
            module_file = hooks.get_module_file_attribute(self.namespace + '.QtWebEngineCore')
            for lib_name, lib_path in bindepend.get_imports(module_file):  # (name, fullpath) tuples
                if lib_path is None:
                    continue  # Skip unresolved libraries
                # Look for ``libnss3.so``.
                if os.path.basename(lib_path).startswith('libnss3.so'):
                    # Find the location of NSS: given a ``/path/to/libnss.so``, search ``/path/to/nss/*.so`` to get the
                    # missing NSS libraries.
                    nss_glob = os.path.join(os.path.dirname(lib_path), 'nss', '*.so')
                    if glob.glob(nss_glob):
                        binaries.append((nss_glob, 'nss'))

        return binaries, datas


# Provide single instances of this class to avoid each hook constructing its own.
pyqt5_library_info = QtLibraryInfo('PyQt5')
pyqt6_library_info = QtLibraryInfo('PyQt6')
pyside2_library_info = QtLibraryInfo('PySide2')
pyside6_library_info = QtLibraryInfo('PySide6')


def get_qt_library_info(namespace):
    """
    Return QtLibraryInfo instance for the given namespace.
    """
    if namespace == 'PyQt5':
        return pyqt5_library_info
    if namespace == 'PyQt6':
        return pyqt6_library_info
    elif namespace == 'PySide2':
        return pyside2_library_info
    elif namespace == 'PySide6':
        return pyside6_library_info

    raise ValueError(f'Invalid namespace: {namespace}!')


# add_qt_dependencies
# --------------------
# Generic implemnentation that finds the Qt 5/6 dependencies based on the hook name of a PyQt5/PyQt6/PySide2/PySide6
# hook. Returns (hiddenimports, binaries, datas). Typical usage:
# ``hiddenimports, binaries, datas = add_qt5_dependencies(__file__)``.
def add_qt_dependencies(hook_file):
    # Find the module underlying this Qt hook: change ``/path/to/hook-PyQt5.blah.py`` to ``PyQt5.blah``.
    hook_name, hook_ext = os.path.splitext(os.path.basename(hook_file))
    assert hook_ext.startswith('.py')
    assert hook_name.startswith('hook-')
    module_name = hook_name[5:]
    namespace = module_name.split('.')[0]

    # Retrieve Qt library info structure....
    qt_info = get_qt_library_info(namespace)
    # ... and use it to collect module dependencies
    return qt_info.collect_module(module_name)


# add_qt5_dependencies
# --------------------
# Find the Qt5 dependencies based on the hook name of a PySide2/PyQt5 hook. Returns (hiddenimports, binaries, datas).
# Typical usage: ``hiddenimports, binaries, datas = add_qt5_dependencies(__file__)``.
add_qt5_dependencies = add_qt_dependencies  # Use generic implementation

# add_qt6_dependencies
# --------------------
# Find the Qt6 dependencies based on the hook name of a PySide6/PyQt6 hook. Returns (hiddenimports, binaries, datas).
# Typical usage: ``hiddenimports, binaries, datas = add_qt6_dependencies(__file__)``.
add_qt6_dependencies = add_qt_dependencies  # Use generic implementation
