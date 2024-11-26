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
"""
Hook for PyZMQ. Cython based Python bindings for messaging library ZeroMQ.
http://www.zeromq.org/
"""
import os
import glob
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import is_module_satisfies, get_module_file_attribute
from PyInstaller.compat import is_win

binaries = []
datas = []
hiddenimports = ['zmq.utils.garbage']

# PyZMQ comes with two backends, cython and cffi. Calling collect_submodules()
# on zmq.backend seems to trigger attempt at compilation of C extension
# module for cffi backend, which will fail if ZeroMQ development files
# are not installed on the system. On non-English locales, the resulting
# localized error messages may cause UnicodeDecodeError. Collecting each
# backend individually, however, does not seem to cause any problems.
hiddenimports += ['zmq.backend']

# cython backend
hiddenimports += collect_submodules('zmq.backend.cython')

# cffi backend: contains extra data that needs to be collected
# (e.g., _cdefs.h)
#
# NOTE: the cffi backend requires compilation of C extension at runtime,
# which appears to be broken in frozen program. So avoid collecting
# it altogether...
if False:
    from PyInstaller.utils.hooks import collect_data_files

    hiddenimports += collect_submodules('zmq.backend.cffi')
    datas += collect_data_files('zmq.backend.cffi', excludes=['**/__pycache__', ])

# Starting with pyzmq 22.0.0, the DLLs in Windows wheel are located in
# site-packages/pyzmq.libs directory along with a .load_order file. This
# file is required on python 3.7 and earlier. On later versions of python,
# the pyzmq.libs is required to exist.
if is_win and is_module_satisfies('pyzmq >= 22.0.0'):
    zmq_root = os.path.dirname(get_module_file_attribute('zmq'))
    libs_dir = os.path.join(zmq_root, os.path.pardir, 'pyzmq.libs')
    # .load_order file (22.0.3 replaced underscore with dash and added
    # version suffix on this file, hence the glob)
    load_order_file = glob.glob(os.path.join(libs_dir, '.load*'))
    datas += [(filename, 'pyzmq.libs') for filename in load_order_file]
    # We need to collect DLLs into _MEIPASS, to avoid duplication due to
    # subsequent binary analysis
    dll_files = glob.glob(os.path.join(libs_dir, "*.dll"))
    binaries += [(dll_file, '.') for dll_file in dll_files]
