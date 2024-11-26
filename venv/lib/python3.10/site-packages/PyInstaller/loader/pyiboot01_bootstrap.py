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

#-- Start bootstrap process
# Only python built-in modules can be used.

import sys

import pyimod02_importers

# Extend Python import machinery by adding PEP302 importers to sys.meta_path.
pyimod02_importers.install()

#-- Bootstrap process is complete.
# We can use other python modules (e.g. os)

import os  # noqa: E402

# Let other python modules know that the code is running in frozen mode.
if not hasattr(sys, 'frozen'):
    sys.frozen = True

# sys._MEIPASS is now set in the bootloader. Hooray.

# Python 3 C-API function Py_SetPath() resets sys.prefix to empty string. Python 2 was using PYTHONHOME for sys.prefix.
# Let's do the same for Python 3.
sys.prefix = sys._MEIPASS
sys.exec_prefix = sys.prefix

# Python 3.3+ defines also sys.base_prefix. Let's set them too.
sys.base_prefix = sys.prefix
sys.base_exec_prefix = sys.exec_prefix

# Some packages behave differently when running inside virtual environment. E.g., IPython tries to append path
# VIRTUAL_ENV to sys.path. For the frozen app we want to prevent this behavior.
VIRTENV = 'VIRTUAL_ENV'
if VIRTENV in os.environ:
    # On some platforms (e.g., AIX) 'os.unsetenv()' is unavailable and deleting the var from os.environ does not
    # delete it from the environment.
    os.environ[VIRTENV] = ''
    del os.environ[VIRTENV]

# Ensure sys.path contains absolute paths. Otherwise, import of other python modules will fail when current working
# directory is changed by the frozen application.
python_path = []
for pth in sys.path:
    python_path.append(os.path.abspath(pth))
    sys.path = python_path

# At least on Windows, Python seems to hook up the codecs on this import, so it is not enough to just package up all
# the encodings.
#
# It was also reported that without 'encodings' module, the frozen executable fails to load in some configurations:
# http://www.pyinstaller.org/ticket/651
#
# Importing 'encodings' module in a run-time hook is not enough, since some run-time hooks require this module, and the
# order of running the code from the run-time hooks is not defined.
try:
    import encodings  # noqa: F401
except ImportError:
    pass

# In the Python interpreter 'warnings' module is imported when 'sys.warnoptions' is not empty. Mimic this behavior.
if sys.warnoptions:
    import warnings  # noqa: F401

# Install the hooks for ctypes
import pyimod03_ctypes  # noqa: E402

pyimod03_ctypes.install()

# Install the hooks for pywin32 (Windows only)
if sys.platform.startswith('win'):
    import pyimod04_pywin32
    pyimod04_pywin32.install()

# Apply a hack for metadata that was collected from (unzipped) python eggs; the EGG-INFO directories are collected into
# their parent directories (my_package-version.egg/EGG-INFO), and for metadata to be discoverable by
# `importlib.metadata`, the .egg directory needs to be in `sys.path`. The deprecated `pkg_resources` does not have this
# limitation, and seems to work as long as the .egg directory's parent directory (in our case `sys._MEIPASS` is in
# `sys.path`.
for entry in os.listdir(sys._MEIPASS):
    entry = os.path.join(sys._MEIPASS, entry)
    if not os.path.isdir(entry):
        continue
    if entry.endswith('.egg'):
        sys.path.append(entry)
