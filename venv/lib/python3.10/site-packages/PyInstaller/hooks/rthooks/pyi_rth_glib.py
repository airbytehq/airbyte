#-----------------------------------------------------------------------------
# Copyright (c) 2015-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------


def _pyi_rthook():
    import os
    import sys

    # Prepend the frozen application's data dir to XDG_DATA_DIRS. We need to avoid overwriting the existing paths in
    # order to allow the frozen application to run system-installed applications (for example, launch a web browser via
    # the webbrowser module on Linux). Should the user desire complete isolation of the frozen application from the
    # system, they need to clean up XDG_DATA_DIRS at the start of their program (i.e., remove all entries but first).
    pyi_data_dir = os.path.join(sys._MEIPASS, 'share')

    xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', None)
    if xdg_data_dirs:
        if pyi_data_dir not in xdg_data_dirs:
            xdg_data_dirs = pyi_data_dir + os.pathsep + xdg_data_dirs
    else:
        xdg_data_dirs = pyi_data_dir
    os.environ['XDG_DATA_DIRS'] = xdg_data_dirs

    # Cleanup aux variables
    del xdg_data_dirs
    del pyi_data_dir


_pyi_rthook()
del _pyi_rthook
