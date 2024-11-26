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

import sys
import os
import glob
import pathlib

import PyInstaller.utils.hooks as hookutils
from PyInstaller import compat

hiddenimports = ['numpy']

# On Windows, make sure that opencv_videoio_ffmpeg*.dll is bundled
binaries = []
if compat.is_win:
    # If conda is active, look for the DLL in its library path
    if compat.is_conda:
        libdir = os.path.join(compat.base_prefix, 'Library', 'bin')
        pattern = os.path.join(libdir, 'opencv_videoio_ffmpeg*.dll')
        for f in glob.glob(pattern):

            binaries.append((f, '.'))

    # Include any DLLs from site-packages/cv2 (opencv_videoio_ffmpeg*.dll
    # can be found there in the PyPI version)
    binaries += hookutils.collect_dynamic_libs('cv2')

# Collect auxiliary sub-packages, such as `cv2.gapi`, `cv2.mat_wrapper`, `cv2.misc`, and `cv2.utils`. This also
# picks up submodules with valid module names, such as `cv2.config`, `cv2.load_config_py2`, and `cv2.load_config_py3`.
# Therefore, filter out `cv2.load_config_py2`.
hiddenimports += hookutils.collect_submodules('cv2', filter=lambda name: name != 'cv2.load_config_py2')

# We also need to explicitly exclude `cv2.load_config_py2` due to it being imported in `cv2.__init__`.
excludedimports = ['cv2.load_config_py2']

# OpenCV loader from 4.5.4.60 requires extra config files and modules.
# We need to collect `config.py`  and `load_config_py3`; to improve compatibility with PyInstaller < 5.2, where
# `module_collection_mode` (see below) is not implemented.
# We also need to collect `config-3.py` or `config-3.X.py`, whichever is available (the former is usually
# provided by PyPI wheels, while the latter seems to be used when user builds OpenCV from source).
datas = hookutils.collect_data_files(
    'cv2',
    include_py_files=True,
    includes=[
        'config.py',
        f'config-{sys.version_info[0]}.{sys.version_info[1]}.py',
        'config-3.py',
        'load_config_py3.py',
    ],
)


# The OpenCV versions that attempt to perform module substitution via sys.path manipulation (== 4.5.4.58, >= 4.6.0.66)
# do not directly import the cv2.cv2 extension anymore, so in order to ensure it is collected, we would need to add it
# to hidden imports. However, when OpenCV is built by user from source, the extension is not located in the package's
# root directory, but in python-3.X sub-directory, which precludes referencing via module name due to sub-directory
# not being a valid subpackage name. Hence, emulate the OpenCV's loader and execute `config-3.py` or `config-3.X.py`
# to obtain the search path.
def find_cv2_extension(config_file):
    # Prepare environment
    PYTHON_EXTENSIONS_PATHS = []
    LOADER_DIR = os.path.dirname(os.path.abspath(os.path.realpath(config_file)))

    global_vars = globals().copy()
    local_vars = locals().copy()

    # Exec the config file
    with open(config_file) as fp:
        code = compile(fp.read(), os.path.basename(config_file), 'exec')
    exec(code, global_vars, local_vars)

    # Read the modified PYTHON_EXTENSIONS_PATHS
    PYTHON_EXTENSIONS_PATHS = local_vars['PYTHON_EXTENSIONS_PATHS']
    if not PYTHON_EXTENSIONS_PATHS:
        return None

    # Search for extension file
    for extension_path in PYTHON_EXTENSIONS_PATHS:
        extension_path = pathlib.Path(extension_path)
        if compat.is_win:
            extension_files = list(extension_path.glob('cv2*.pyd'))
        else:
            extension_files = list(extension_path.glob('cv2*.so'))
        if extension_files:
            if len(extension_files) > 1:
                hookutils.logger.warning("Found multiple cv2 extension candidates: %s", extension_files)
            extension_file = extension_files[0]  # Take first (or hopefully the only one)

            hookutils.logger.debug("Found cv2 extension module: %s", extension_file)

            # Compute path relative to parent of config file (which should be the package's root)
            dest_dir = pathlib.Path("cv2") / extension_file.parent.relative_to(LOADER_DIR)
            return str(extension_file), str(dest_dir)

    hookutils.logger.warning(
        "Could not find cv2 extension module! Config file: %s, search paths: %s",
        config_file, PYTHON_EXTENSIONS_PATHS)

    return None


config_file = [
    src_path for src_path, _ in datas
    if os.path.basename(src_path) in (f'config-{sys.version_info[0]}.{sys.version_info[1]}.py', 'config-3.py')
]

if config_file:
    try:
        extension_info = find_cv2_extension(config_file[0])
        if extension_info:
            ext_src, ext_dst = extension_info
            # Due to bug in PyInstaller's TOC structure implementation (affecting PyInstaller up to latest version at
            # the time of writing, 5.9), we fail to properly resolve `cv2.cv2` EXTENSION entry's destination name if
            # we already have a BINARY entry with the same destination name. This results in verbatim `cv2.cv2` file
            # created in application directory in addition to the proper copy in the `cv2` sub-directoy.
            # Therefoe, if destination directory of the cv2 extension module is the top-level package directory, fall
            # back to using hiddenimports instead.
            if ext_dst == 'cv2':
                # Extension found in top-level package directory; likely a PyPI wheel.
                hiddenimports += ['cv2.cv2']
            else:
                # Extension found in sub-directory; use BINARY entry
                binaries += [extension_info]
    except Exception:
        hookutils.logger.warning("Failed to determine location of cv2 extension module!", exc_info=True)


# Mark the cv2 package to be collected in source form, bypassing PyInstaller's PYZ archive and FrozenImporter. This is
# necessary because recent versions of cv2 package attempt to perform module substritution via sys.path manipulation,
# which is incompatible with the way that FrozenImporter works. This requires pyinstaller/pyinstaller#6945, i.e.,
# PyInstaller >= 5.3. On earlier versions, the following statement does nothing, and problematic cv2 versions
# (== 4.5.4.58, >= 4.6.0.66) will not work.
#
# Note that the collect_data_files() above is still necessary, because some of the cv2 loader's config scripts are not
# valid module names (e.g., config-3.py). So the two collection approaches are complementary, and any overlap in files
# (e.g., __init__.py) is handled gracefully due to PyInstaller's uniqueness constraints on collected files.
module_collection_mode = 'py'

# In linux PyPI opencv-python wheels, the cv2 extension is linked against Qt, and the wheel bundles a basic subset of Qt
# shared libraries, plugins, and font files. This is not the case on other OSes (presumably native UI APIs are used by
# OpenCV HighGUI module), nor in the headless PyPI wheels (opencv-python-headless).
# The bundled Qt shared libraries should be picked up automatically due to binary dependency analysis, but we need to
# collect plugins and font files from the `qt` subdirectory.
if compat.is_linux:
    pkg_path = pathlib.Path(hookutils.get_module_file_attribute('cv2')).parent
    # Collect .ttf files fron fonts directory.
    # NOTE: since we are using glob, we can skip checks for (sub)directories' existence.
    qt_fonts_dir = pkg_path / 'qt' / 'fonts'
    datas += [
        (str(font_file), str(font_file.parent.relative_to(pkg_path.parent)))
        for font_file in qt_fonts_dir.rglob('*.ttf')
    ]
    # Collect .so files from plugins directory.
    qt_plugins_dir = pkg_path / 'qt' / 'plugins'
    binaries += [
        (str(plugin_file), str(plugin_file.parent.relative_to(pkg_path.parent)))
        for plugin_file in qt_plugins_dir.rglob('*.so')
    ]
