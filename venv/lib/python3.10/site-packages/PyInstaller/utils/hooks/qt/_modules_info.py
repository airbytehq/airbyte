# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

# Qt modules information - the core of our Qt collection approach
# ----------------------------------------------------------------
#
# The python bindings for Qt (``PySide2``, ``PyQt5``, ``PySide6``, ``PyQt6``) consist of several python binary extension
# modules that provide bindings for corresponding Qt modules. For example, the ``PySide2.QtNetwork`` python extension
# module provides bindings for the ``QtNetwork`` Qt module from the ``qt/qtbase`` Qt repository.
#
# A Qt module can be considered as consisting of:
#  * a shared library (for example, on Linux, the shared library names for the ``QtNetwork`` Qt module in Qt5 and Qt6
#    are ``libQt5Network.so`` and ``libQt6Network.so``, respectively).
#  * plugins: a certain type (or class) of plugins is usually associated with a single Qt module (for example,
#    ``imageformats`` plugins are associated with the ``QtGui`` Qt module from the ``qt/qtbase`` Qt repository), but
#    additional plugins of that type may come from other Qt repositories. For example, ``imageformats/qsvg`` plugin
#    is provided by ``qtsvg/src/plugins/imageformats/svg`` from the ``qt/qtsvg`` repository, and ``imageformats/qpdf``
#    is provided by ``qtwebengine/src/pdf/plugins/imageformats/pdf`` from the ``qt/qtwebengine`` repository.
#  * translation files: names of translation files consist of a base name, which typically corresponds to the Qt
#    repository name, and language code. A single translation file usually covers all Qt modules contained within
#    the same repository. For example, translation files with base name ``qtbase``  contain translations for ``QtCore``,
#    ``QtGui``, ``QtWidgets``, ``QtNetwork``, and other Qt modules from the ``qt/qtbase`` Qt repository.
#
# The PyInstaller's built-in analysis of link-time dependencies ensures that when collecting a Qt python extension
# module, we automatically pick up the linked Qt shared libraries. However, collection of linked Qt shared libraries
# does not result in collection of plugins, nor translation files. In addition, the dependency of a Qt python extension
# module on other Qt python extension modules (i.e., at the bindings level) cannot be automatically determined due to
# PyInstaller's inability to scan imports in binary extensions.
#
# PyInstaller < 5.7 solved this problem using a dictionary that associated a Qt shared library name with python
# extension name, plugins, and translation files. For each hooked Qt python extension module, the hook calls a helper
# that analyzes the extension file for link-time dependencies, and matches those against the dictionary. Therefore,
# based on linked shared libraries, we could recursively infer the list of files to collect in addition to the shared
# libraries themselves:
#  - plugins and translation files belonging to Qt modules whose shared libraries we collect
#  - Qt python extension modules corresponding to the Qt modules that we collect
#
# The above approach ensures that even if analyzed python script contains only ``from PySide2 import QtWidgets``,
# we would also collect ``PySide2.QtGui`` and ``PySide2.QtCore``, as well as all corresponding Qt module files
# (the shared libraries, plugins, translation files). For this to work, a hook must be provided for the
# ``PySide2.QtWidgets`` that performs the recursive analysis of the extension module file; so to ensure that each
# Qt python extension module by itself ensures collection of all its dependencies, we need to hook all Qt python
# extension modules provided by specific python Qt bindings package.
#
# The above approach with single dictionary, however, has several limitations:
#  - it cannot provide association for Qt python module that binds a Qt module without a shared library (i.e., a
#    headers-only module, or a statically-built module). In such cases, potential plugins and translations should
#    be associated directly with the Qt python extension file instead of the Qt module's (non-existent) shared library.
#  - it cannot (directly) handle differences between Qt5 and Qt6; we had to build a second dictionary
#  - it cannot handle differences between the bindings themselves; for example, PyQt5 binds some Qt modules that
#    PySide2 does not bind. Or, the binding's Qt python extension module is named differently in PyQt and PySide
#    bindings (or just differently in PyQt5, while PySide2, PySide6, and PyQt6 use the same name).
#
# In order address the above shortcomings, we now store all information a list of structures that contain information
# for a particular Qt python extension and/or Qt module (shared library):
#  - python extension name (if applicable)
#  - Qt module name base (if applicable)
#  - plugins
#  - translation files base name
#  - applicable Qt version (if necessary)
#  - applicable Qt bindings (if necessary)
#
# This list is used to dynamically construct two dictionaries (based on the bindings name and Qt version):
#  - mapping python extension names to associated module information
#  - mapping Qt shared library names to associated module information
# This allows us to associate plugins and translations with either Qt python extension or with the Qt module's shared
# library (or both), whichever is applicable.
#
# The `qt_dynamic_dependencies_dict`_ from the original approach was constructed using several information sources, as
# documented `here
# <https://github.com/pyinstaller/pyinstaller/blob/fbf7948be85177dd44b41217e9f039e1d176de6b/PyInstaller/utils/hooks/qt.py#L266-L362>˙_.
#
# In the current approach, the relations stored in the `QT_MODULES_INFO`_ list were determined directly, by inspecting
# the Qt source code. This requires some prior knowledge of how the Qt code is organized (repositories and individual Qt
# modules within them), as well as some searching based on guesswork. The procedure can be outlined as follows:
#  * check out the `main Qt repository <git://code.qt.io/qt/qt5.git>`_. This repository contains references to all other
#    Qt repositories in the form of git submodules.
#  * for Qt5:
#      * check out the latest release tag, e.g., v5.15.2, then check out the submodules.
#      * search the Qt modules' qmake .pro files; for example, ``qtbase/src/network/network.pro`` for QtNetwork module.
#        The plugin types associated with the module are listed in the ``MODULE_PLUGIN_TYPES`` variable (in this case,
#        ``bearer``).
#      * all translations are gathered in ``qttranslations`` sub-module/repository, and their association with
#        individual repositories can be seen in ``qttranslations/translations/translations.pro``.
#  * for Qt6:
#      * check out the latest release tag, e.g., v6.3.1, then check out the submodules.
#      * search the Qt modules' CMake files; for example, ``qtbase/src/network/CMakeLists.txt`` for QtNetwork module.
#        The plugin types associated with the module are listed under ``PLUGIN_TYPES`` argument of the
#        ``qt_internal_add_module()`` function that defines the Qt module.
#
# The idea is to make a list of all extension modules found in a Qt bindings package, as well as all available plugin
# directories (which correspond to plugin types) and translation files. For each extension, identify the corresponding
# Qt module (shared library name) and its associated plugins and translation files. Once this is done, most of available
# plugins and translations in the python bindings package should have a corresponding python Qt extension module
# available; this gives us associations based on the python extension module names as well as based on the Qt shared
# library names. For any plugins and translation files remaining unassociated, identify the corresponding Qt module;
# this gives us associations based only on Qt shared library names. While this second group of associations are never
# processed directly (due to lack of corresponding python extension), they may end up being processed during the
# recursive dependency analysis, if the corresponding Qt shared library is linked against by some Qt python extension
# or another Qt shared library.


# This structure is used to define Qt module information, such as python module/extension name, Qt module (shared
# library) name, translation files' base names, plugins, as well as associated python bindings (which implicitly
# also encode major Qt version).
class _QtModuleDef:
    def __init__(self, module, shared_lib=None, translations=None, plugins=None, bindings=None):
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
        # List of bindings (PySide2, PyQt5, PySide6, PyQt6) that provide the python module. This allows association of
        # plugins and translations with shared libraries even for bindings that do not provide python module binding
        # for the Qt module.
        self.bindings = set(bindings or [])


# All Qt-based bindings.
ALL_QT_BINDINGS = {"PySide2", "PyQt5", "PySide6", "PyQt6"}

# Qt modules information - the core of our Qt collection approach.
#
# For every python module/extension (i.e., entry in the list below that has valid `module`), we need a corresponding
# hook, ensuring that the extension file is analyzed, so that we collect the associated plugins and translation
# files, as well as perform recursive analysis of link-time binary dependencies (so that plugins and translation files
# belonging to those dependencies are collected as well).
QT_MODULES_INFO = (
    # *** qt/qt3d ***
    _QtModuleDef("Qt3DAnimation", shared_lib="3DAnimation"),
    _QtModuleDef("Qt3DCore", shared_lib="3DCore"),
    _QtModuleDef("Qt3DExtras", shared_lib="3DExtras"),
    _QtModuleDef("Qt3DInput", shared_lib="3DInput", plugins=["3dinputdevices"]),
    _QtModuleDef("Qt3DLogic", shared_lib="3DLogic"),
    _QtModuleDef(
        "Qt3DRender", shared_lib="3DRender", plugins=["geometryloaders", "renderplugins", "renderers", "sceneparsers"]
    ),

    # *** qt/qtactiveqt ***
    # The python module is called QAxContainer in PyQt bindings, but QtAxContainer in PySide. The associated Qt module
    # is header-only, so there is no shared library.
    _QtModuleDef("QAxContainer", bindings=["PyQt*"]),
    _QtModuleDef("QtAxContainer", bindings=["PySide*"]),

    # *** qt/qtcharts ***
    # The python module is called QtChart in PyQt5, and QtCharts in PySide2, PySide6, and PyQt6 (which corresponds to
    # the associated Qt module name, QtCharts).
    _QtModuleDef("QtChart", shared_lib="Charts", bindings=["PyQt5"]),
    _QtModuleDef("QtCharts", shared_lib="Charts", bindings=["!PyQt5"]),

    # *** qt/qtbase ***
    # QtConcurrent python module is available only in PySide bindings.
    _QtModuleDef(None, shared_lib="Concurrent", bindings=["PyQt*"]),
    _QtModuleDef("QtConcurrent", shared_lib="Concurrent", bindings=["PySide*"]),
    _QtModuleDef("QtCore", shared_lib="Core", translations=["qt", "qtbase"]),
    # QtDBus python module is available in all bindings but PySide2.
    _QtModuleDef(None, shared_lib="DBus", bindings=["PySide2"]),
    _QtModuleDef("QtDBus", shared_lib="DBus", bindings=["!PySide2"]),
    # QtNetwork uses different plugins in Qt5 and Qt6.
    _QtModuleDef("QtNetwork", shared_lib="Network", plugins=["bearer"], bindings=["PySide2", "PyQt5"]),
    _QtModuleDef(
        "QtNetwork",
        shared_lib="Network",
        plugins=["networkaccess", "networkinformation", "tls"],
        bindings=["PySide6", "PyQt6"]
    ),
    _QtModuleDef(
        "QtGui",
        shared_lib="Gui",
        plugins=[
            "accessiblebridge",
            "egldeviceintegrations",
            "generic",
            "iconengines",
            "imageformats",
            "platforms",
            "platforms/darwin",
            "platforminputcontexts",
            "platformthemes",
            "xcbglintegrations",
            # The ``wayland-*`` plugins are part of QtWaylandClient Qt module, whose shared library
            # (e.g., libQt5WaylandClient.so) is linked by the wayland-related ``platforms`` plugins. Ideally, we would
            # collect these plugins based on the QtWaylandClient shared library entry, but as our Qt hook utilities do
            # not scan the plugins for dependencies, that would not work. So instead we list these plugins under QtGui
            # to achieve pretty much the same end result.
            "wayland-decoration-client",
            "wayland-graphics-integration-client",
            "wayland-shell-integration"
        ]
    ),
    _QtModuleDef("QtOpenGL", shared_lib="OpenGL"),
    # This python module is specific to PySide2 and has no associated Qt module.
    _QtModuleDef("QtOpenGLFunctions", bindings=["PySide2"]),
    # This Qt module was introduced with Qt6.
    _QtModuleDef("QtOpenGLWidgets", shared_lib="OpenGLWidgets", bindings=["PySide6", "PyQt6"]),
    _QtModuleDef("QtPrintSupport", shared_lib="PrintSupport", plugins=["printsupport"]),
    _QtModuleDef("QtSql", shared_lib="Sql", plugins=["sqldrivers"]),
    _QtModuleDef("QtTest", shared_lib="Test"),
    _QtModuleDef("QtWidgets", shared_lib="Widgets", plugins=["styles"]),
    _QtModuleDef("QtXml", shared_lib="Xml"),

    # *** qt/qtconnectivity ***
    _QtModuleDef("QtBluetooth", shared_lib="QtBluetooth", translations=["qtconnectivity"]),
    _QtModuleDef("QtNfc", shared_lib="Nfc", translations=["qtconnectivity"]),

    # *** qt/qtdatavis3d ***
    _QtModuleDef("QtDataVisualization", shared_lib="DataVisualization"),

    # *** qt/qtdeclarative ***
    _QtModuleDef("QtQml", shared_lib="Qml", translations=["qtdeclarative"], plugins=["qmltooling"]),
    # Have the Qt5 variant collect translations for qtquickcontrols (qt/qtquickcontrols provides only QtQuick plugins).
    _QtModuleDef(
        "QtQuick",
        shared_lib="Quick",
        translations=["qtquickcontrols"],
        plugins=["scenegraph"],
        bindings=["PySide2", "PyQt5"]
    ),
    _QtModuleDef("QtQuick", shared_lib="Quick", plugins=["scenegraph"], bindings=["PySide6", "PyQt6"]),
    # Qt6-only; in Qt5, this module is part of qt/qtquickcontrols2. Python module is available only in PySide6.
    _QtModuleDef(None, shared_lib="QuickControls2", bindings=["PyQt6"]),
    _QtModuleDef("QtQuickControls2", shared_lib="QuickControls2", bindings=["PySide6"]),
    _QtModuleDef("QtQuickWidgets", shared_lib="QuickWidgets"),

    # *** qt/qtgamepad ***
    # No python module; shared library -> plugins association entry.
    _QtModuleDef(None, shared_lib="Gamepad", plugins=["gamepads"]),

    # *** qt/qtgraphs ***
    # Qt6 >= 6.6.0; python module is available only in PySide6.
    _QtModuleDef("QtGraphs", shared_lib="Graphs", bindings=["PySide6"]),

    # *** qt/qthttpserver ***
    # Qt6 >= 6.4.0; python module is available only in PySide6.
    _QtModuleDef("QtHttpServer", shared_lib="HttpServer", bindings=["PySide6"]),

    # *** qt/qtlocation ***
    # QtLocation was reintroduced in Qt6 v6.5.0.
    _QtModuleDef(
        "QtLocation",
        shared_lib="Location",
        translations=["qtlocation"],
        plugins=["geoservices"],
        bindings=["PySide2", "PyQt5", "PySide6"]
    ),
    _QtModuleDef(
        "QtPositioning",
        shared_lib="Positioning",
        translations=["qtlocation"],
        plugins=["position"],
    ),

    # *** qt/qtmacextras ***
    # Qt5-only Qt module.
    _QtModuleDef("QtMacExtras", shared_lib="MacExtras", bindings=["PySide2", "PyQt5"]),

    # *** qt/qtmultimedia ***
    # QtMultimedia on Qt6 currently uses only a subset of plugin names from Qt5 counterpart.
    _QtModuleDef(
        "QtMultimedia",
        shared_lib="Multimedia",
        translations=["qtmultimedia"],
        plugins=[
            "mediaservice", "audio", "video/bufferpool", "video/gstvideorenderer", "video/videonode", "playlistformats",
            "resourcepolicy"
        ],
        bindings=["PySide2", "PyQt5"]
    ),
    _QtModuleDef(
        "QtMultimedia",
        shared_lib="Multimedia",
        translations=["qtmultimedia"],
        # `multimedia` plugins are available as of Qt6 >= 6.4.0; earlier versions had `video/gstvideorenderer` and
        # `video/videonode` plugins.
        plugins=["multimedia", "video/gstvideorenderer", "video/videonode"],
        bindings=["PySide6", "PyQt6"]
    ),
    _QtModuleDef("QtMultimediaWidgets", shared_lib="MultimediaWidgets"),
    # Qt6-only Qt module; python module is available in PySide6 >= 6.4.0 and PyQt6 >= 6.5.0
    _QtModuleDef("QtSpatialAudio", shared_lib="SpatialAudio", bindings=["PySide6", "PyQt6"]),

    # *** qt/qtnetworkauth ***
    # QtNetworkAuth python module is available in all bindings but PySide2.
    _QtModuleDef(None, shared_lib="NetworkAuth", bindings=["PySide2"]),
    _QtModuleDef("QtNetworkAuth", shared_lib="NetworkAuth", bindings=["!PySide2"]),

    # *** qt/qtpurchasing ***
    # Qt5-only Qt module, python module is available only in PyQt5.
    _QtModuleDef("QtPurchasing", shared_lib="Purchasing", bindings=["PyQt5"]),

    # *** qt/qtquick1 ***
    # This is an old, Qt 5.3-era module...
    _QtModuleDef(
        "QtDeclarative",
        shared_lib="Declarative",
        translations=["qtquick1"],
        plugins=["qml1tooling"],
        bindings=["PySide2", "PyQt5"]
    ),

    # *** qt/qtquick3d ***
    # QtQuick3D python module is available in all bindings but PySide2.
    _QtModuleDef(None, shared_lib="Quick3D", bindings=["PySide2"]),
    _QtModuleDef("QtQuick3D", shared_lib="Quick3D", bindings=["!PySide2"]),
    # No python module; shared library -> plugins association entry.
    _QtModuleDef(None, shared_lib="Quick3DAssetImport", plugins=["assetimporters"]),

    # *** qt/qtquickcontrols2 ***
    # Qt5-only module; in Qt6, this module is part of qt/declarative. Python module is available only in PySide2.
    _QtModuleDef(None, translations=["qtquickcontrols2"], shared_lib="QuickControls2", bindings=["PyQt5"]),
    _QtModuleDef(
        "QtQuickControls2", translations=["qtquickcontrols2"], shared_lib="QuickControls2", bindings=["PySide2"]
    ),

    # *** qt/qtremoteobjects ***
    _QtModuleDef("QtRemoteObjects", shared_lib="RemoteObjects"),

    # *** qt/qtscxml ***
    # Python module is available only in PySide bindings. Plugins are available only in Qt6.
    # PyQt wheels do not seem to ship the corresponding Qt modules (shared libs) at all.
    _QtModuleDef("QtScxml", shared_lib="Scxml", bindings=["PySide2"]),
    _QtModuleDef("QtScxml", shared_lib="Scxml", plugins=["scxmldatamodel"], bindings=["PySide6"]),
    # Qt6-only Qt module, python module is available only in PySide6.
    _QtModuleDef("QtStateMachine", shared_lib="StateMachine", bindings=["PySide6"]),

    # *** qt/qtsensors ***
    _QtModuleDef("QtSensors", shared_lib="Sensors", plugins=["sensors", "sensorgestures"]),

    # *** qt/qtserialport ***
    _QtModuleDef("QtSerialPort", shared_lib="SerialPort", translations=["qtserialport"]),

    # *** qt/qtscript ***
    # Qt5-only Qt module, python module is available only in PySide2. PyQt5 wheels do not seem to ship the corresponding
    # Qt modules (shared libs) at all.
    _QtModuleDef("QtScript", shared_lib="Script", translations=["qtscript"], plugins=["script"], bindings=["PySide2"]),
    _QtModuleDef("QtScriptTools", shared_lib="ScriptTools", bindings=["PySide2"]),

    # *** qt/qtserialbus ***
    # No python module; shared library -> plugins association entry.
    # PySide6 6.5.0 introduced python module.
    _QtModuleDef(None, shared_lib="SerialBus", plugins=["canbus"], bindings=["!PySide6"]),
    _QtModuleDef("QtSerialBus", shared_lib="SerialBus", plugins=["canbus"], bindings=["PySide6"]),

    # *** qt/qtsvg ***
    _QtModuleDef("QtSvg", shared_lib="Svg"),
    # Qt6-only Qt module.
    _QtModuleDef("QtSvgWidgets", shared_lib="SvgWidgets", bindings=["PySide6", "PyQt6"]),

    # *** qt/qtspeech ***
    _QtModuleDef("QtTextToSpeech", shared_lib="TextToSpeech", plugins=["texttospeech"]),

    # *** qt/qttools ***
    # QtDesigner python module is available in all bindings but PySide2.
    _QtModuleDef(None, shared_lib="Designer", plugins=["designer"], bindings=["PySide2"]),
    _QtModuleDef(
        "QtDesigner", shared_lib="Designer", translations=["designer"], plugins=["designer"], bindings=["!PySide2"]
    ),
    _QtModuleDef("QtHelp", shared_lib="Help", translations=["qt_help"]),
    # Python module is available only in PySide bindings.
    _QtModuleDef("QtUiTools", shared_lib="UiTools", bindings=["PySide*"]),

    # *** qt/qtvirtualkeyboard ***
    # No python module; shared library -> plugins association entry.
    _QtModuleDef(None, shared_lib="VirtualKeyboard", plugins=["virtualkeyboard"]),

    # *** qt/qtwebchannel ***
    _QtModuleDef("QtWebChannel", shared_lib="WebChannel"),

    # *** qt/qtwebengine ***
    # QtWebEngine is Qt5-only module (replaced by QtWebEngineQuick in Qt6).
    _QtModuleDef("QtWebEngine", shared_lib="WebEngine", bindings=["PySide2", "PyQt5"]),
    _QtModuleDef("QtWebEngineCore", shared_lib="WebEngineCore", translations=["qtwebengine"]),
    # QtWebEngineQuick is Qt6-only module (replacement for QtWebEngine in Qt5).
    _QtModuleDef("QtWebEngineQuick", shared_lib="WebEngineQuick", bindings=["PySide6", "PyQt6"]),
    _QtModuleDef("QtWebEngineWidgets", shared_lib="WebEngineWidgets"),
    # QtPdf and QtPdfWidgets have python module available in PySide6 and PyQt6 >= 6.4.0.
    _QtModuleDef("QtPdf", shared_lib="Pdf", bindings=["PySide6", "PyQt6"]),
    _QtModuleDef("QtPdfWidgets", shared_lib="PdfWidgets", bindings=["PySide6", "PyQt6"]),

    # *** qt/qtwebsockets ***
    _QtModuleDef("QtWebSockets", shared_lib="WebSockets", translations=["qtwebsockets"]),

    # *** qt/qtwebview ***
    # No python module; shared library -> plugins association entry.
    _QtModuleDef(None, shared_lib="WebView", plugins=["webview"]),

    # *** qt/qtwinextras ***
    # Qt5-only Qt module.
    _QtModuleDef("QtWinExtras", shared_lib="WinExtras", bindings=["PySide2", "PyQt5"]),

    # *** qt/qtx11extras ***
    # Qt5-only Qt module.
    _QtModuleDef("QtX11Extras", shared_lib="X11Extras", bindings=["PySide2", "PyQt5"]),

    # *** qt/qtxmlpatterns ***
    # Qt5-only Qt module.
    _QtModuleDef(
        "QtXmlPatterns", shared_lib="XmlPatterns", translations=["qtxmlpatterns"], bindings=["PySide2", "PyQt5"]
    ),

    # *** qscintilla ***
    # Python module is available only in PyQt bindings. No associated shared library.
    _QtModuleDef("Qsci", translations=["qscintilla"], bindings=["PyQt*"]),
)


# Helpers for turning Qt namespace specifiers, such as "!PySide2" or "PyQt*", into set of applicable
# namespaces.
def process_namespace_strings(namespaces):
    """"Process list of Qt namespace specifier strings into set of namespaces."""
    bindings = set()
    for namespace in namespaces:
        bindings |= _process_namespace_string(namespace)
    return bindings


def _process_namespace_string(namespace):
    """Expand a Qt namespace specifier string into set of namespaces."""
    if namespace.startswith("!"):
        bindings = _process_namespace_string(namespace[1:])
        return ALL_QT_BINDINGS - bindings
    else:
        if namespace == "PySide*":
            return {"PySide2", "PySide6"}
        elif namespace == "PyQt*":
            return {"PyQt5", "PyQt6"}
        elif namespace in ALL_QT_BINDINGS:
            return {namespace}
        else:
            raise ValueError(f"Invalid Qt namespace specifier: {namespace}!")
