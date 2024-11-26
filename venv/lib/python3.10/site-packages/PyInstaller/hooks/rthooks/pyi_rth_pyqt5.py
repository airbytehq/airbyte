#-----------------------------------------------------------------------------
# Copyright (c) 2014-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

# The path to Qt's components may not default to the wheel layout for self-compiled PyQt5 installations. Mandate the
# wheel layout. See ``utils/hooks/qt.py`` for more details.


def _pyi_rthook():
    import os
    import sys

    from _pyi_rth_utils import is_macos_app_bundle

    # Try PyQt5 5.15.4-style path first...
    pyqt_path = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt5')
    if not os.path.isdir(pyqt_path):
        # ... and fall back to the older version
        pyqt_path = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt')

    os.environ['QT_PLUGIN_PATH'] = os.path.join(pyqt_path, 'plugins')

    if is_macos_app_bundle:
        # Special handling for macOS .app bundles. To satisfy codesign requirements, we are forced to split `qml`
        # directory into two parts; one that keeps only binaries (rooted in `Contents/Frameworks`) and one that keeps
        # only data files (rooted in `Contents/Resources), with files from one directory tree being symlinked to the
        # other to maintain illusion of a single mixed-content directory. As Qt seems to compute the identifier of its
        # QML components based on location of the `qmldir` file w.r.t. the registered QML import paths, we need to
        # register both paths, because the `qmldir` file for a component could be reached via either directory tree.
        pyqt_path_res = os.path.normpath(
            os.path.join(sys._MEIPASS, '..', 'Resources', os.path.relpath(pyqt_path, sys._MEIPASS))
        )
        os.environ['QML2_IMPORT_PATH'] = os.pathsep.join([
            os.path.join(pyqt_path_res, 'qml'),
            os.path.join(pyqt_path, 'qml'),
        ])
    else:
        os.environ['QML2_IMPORT_PATH'] = os.path.join(pyqt_path, 'qml')

    # This is required starting in PyQt5 5.12.3. See discussion in #4293.
    if sys.platform.startswith('win') and 'PATH' in os.environ:
        os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']


_pyi_rthook()
del _pyi_rthook
