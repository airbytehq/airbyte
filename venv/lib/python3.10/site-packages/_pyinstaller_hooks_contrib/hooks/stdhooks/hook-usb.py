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

import ctypes.util
import os

from PyInstaller.depend.utils import _resolveCtypesImports
from PyInstaller.compat import is_cygwin, getenv
from PyInstaller.utils.hooks import logger

# Include glob for library lookup in run-time hook.
hiddenimports = ['glob']

# https://github.com/walac/pyusb/blob/master/docs/faq.rst
# https://github.com/walac/pyusb/blob/master/docs/tutorial.rst

binaries = []

# Running usb.core.find() in this script crashes Ubuntu 14.04LTS,
# let users circumvent pyusb discovery with an environment variable.
skip_pyusb_discovery = \
    bool(getenv('PYINSTALLER_USB_HOOK_SKIP_PYUSB_DISCOVERY'))

# Try to use pyusb's library locator.
if not skip_pyusb_discovery:
    import usb.core
    import usb.backend
    try:
        # get the backend symbols before find
        backend_contents_before_discovery = set(dir(usb.backend))
        # perform find, which will load a usb library if found
        usb.core.find()
        # get the backend symbols which have been added (loaded)
        backends = set(dir(usb.backend)) - backend_contents_before_discovery
        # gather the libraries from the loaded backends
        backend_lib_basenames = []
        for usblib in [getattr(usb.backend, be)._lib for be in backends]:
            if usblib is not None:
                # OSX returns the full path, Linux only the filename.
                # save the basename and reconstruct the path after gathering.
                backend_lib_basenames.append(os.path.basename(usblib._name))
        # try to resolve the library names to absolute paths.
        binaries = _resolveCtypesImports(backend_lib_basenames)
    except (ValueError, usb.core.USBError) as exc:
        logger.warning("%s", exc)

# If pyusb didn't find a backend, manually search for usb libraries.
if not binaries:
    # NOTE: Update these lists when adding further libs.
    if is_cygwin:
        libusb_candidates = ['cygusb-1.0-0.dll', 'cygusb0.dll']
    else:
        libusb_candidates = [
            # libusb10
            'usb-1.0',
            'usb',
            'libusb-1.0',
            # libusb01
            'usb-0.1',
            'libusb0',
            # openusb
            'openusb',
        ]

    backend_library_basenames = []
    for candidate in libusb_candidates:
        libname = ctypes.util.find_library(candidate)
        if libname is not None:
            backend_library_basenames.append(os.path.basename(libname))
    if backend_library_basenames:
        binaries = _resolveCtypesImports(backend_library_basenames)

# Validate and normalize the first found usb library.
if binaries:
    # `_resolveCtypesImports` returns a 3-tuple, but `binaries` are only
    # 2-tuples, so remove the last element:
    assert len(binaries[0]) == 3
    binaries = [(binaries[0][1], '.')]
