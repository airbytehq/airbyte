#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

# matplotlib will create $HOME/.matplotlib folder in user's home directory. In this directory there is fontList.cache
# file which lists paths to matplotlib fonts.
#
# When you run your onefile exe for the first time it's extracted to for example "_MEIxxxxx" temp directory and
# fontList.cache file is created with fonts paths pointing to this directory.
#
# Second time you run your exe new directory is created "_MEIyyyyy" but fontList.cache file still points to previous
# directory which was deleted. And then you will get error like:
#
#     RuntimeError: Could not open facefile
#
# We need to force matplotlib to recreate config directory every time you run your app.


def _pyi_rthook():
    import atexit
    import os
    import shutil

    import _pyi_rth_utils.tempfile  # PyInstaller's run-time hook utilities module

    # Isolate matplotlib's config dir into temporary directory.
    # Use our replacement for `tempfile.mkdtemp` function that properly restricts access to directory on all platforms.
    configdir = _pyi_rth_utils.tempfile.secure_mkdtemp()
    os.environ['MPLCONFIGDIR'] = configdir

    try:
        # Remove temp directory at application exit and ignore any errors.
        atexit.register(shutil.rmtree, configdir, ignore_errors=True)
    except OSError:
        pass


_pyi_rthook()
del _pyi_rthook
