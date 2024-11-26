# ------------------------------------------------------------------
# Copyright (c) 2023 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import os
from PyInstaller.utils.hooks import logger, isolated


def find_library():
    try:
        # the import will fail it the library cannot be found
        from pylsl import pylsl

        # the find_liblsl_libraries() is a generator function that yields multiple possibilities
        for libfile in pylsl.find_liblsl_libraries():
            if libfile:
                break
    except (ImportError, ModuleNotFoundError, RuntimeError) as error:
        print(error)
        libfile = None
    return libfile


# whenever a hook needs to load a 3rd party library, it needs to be done in an isolated subprocess
libfile = isolated.call(find_library)

if libfile:
    # add the liblsl library to the binaries
    # it gets packaged in pylsl/lib, which is where pylsl will look first
    binaries = [(libfile, os.path.join('pylsl', 'lib'))]
else:
    logger.warning("liblsl shared library not found - pylsl will likely fail to work!")
    binaries = []
