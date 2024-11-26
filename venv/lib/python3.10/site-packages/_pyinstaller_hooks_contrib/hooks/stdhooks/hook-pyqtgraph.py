# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files, excluding the examples' data
datas = collect_data_files('pyqtgraph', excludes=['**/examples/*'])

# pyqtgraph uses Qt-version-specific templates for the UI elements.
# There are templates for different versions of PySide and PyQt, e.g.
#
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt6
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyside2
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyside6
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt6
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyside2
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyside6
#
# To be future-proof, we collect all modules by
# using collect-submodules, and filtering the modules
# which appear to be templates.
# We need to avoid recursing into `pyqtgraph.examples`, because that
# triggers instantiation of `QApplication` (which requires X/Wayland
# session on linux).
# Tested with pyqtgraph master branch (commit c1900aa).
all_imports = collect_submodules("pyqtgraph", filter=lambda name: name != "pyqtgraph.examples")
hiddenimports = [name for name in all_imports if "Template" in name]

# Collect the pyqtgraph/multiprocess/bootstrap.py as a module; this is required by our pyqtgraph.multiprocess runtime
# hook to handle the pyqtgraph's multiprocessing implementation. The pyqtgraph.multiprocess seems to be imported
# automatically on the import of pyqtgraph itself, so there is no point in creating a separate hook for this.
hiddenimports += ['pyqtgraph.multiprocess.bootstrap']
