#-----------------------------------------------------------------------------
# Copyright (c) 2022, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

import sys
import os


def _setup_pyqtgraph_multiprocess_hook():
    # NOTE: pyqtgraph.multiprocess spawns the sub-process using subprocess.Popen (or equivalent). This means that in
    # onefile builds, the executable in subprocess will unpack itself again, into different sys._MEIPASS, because
    # the _MEIPASS2 environment variable is not set (bootloader / bootstrap script cleans it up). This will make the
    # argv[1] check below fail, due to different sys._MEIPASS value in the subprocess.
    #
    # To work around this, at the time of writing (PyInstaller 5.5), the user needs to set _MEIPASS2 environment
    # variable to sys._MEIPASS before using `pyqtgraph.multiprocess` in onefile builds. And stlib's
    # `multiprocessing.freeze_support` needs to be called in the entry-point program, due to `pyqtgraph.multiprocess`
    # internally using stdlib's `multiprocessing` primitives.
    if len(sys.argv) == 2 and sys.argv[1] == os.path.join(sys._MEIPASS, 'pyqtgraph', 'multiprocess', 'bootstrap.py'):
        # Load as module; this requires --hiddenimport pyqtgraph.multiprocess.bootstrap
        try:
            mod_name = 'pyqtgraph.multiprocess.bootstrap'
            mod = __import__(mod_name)
            bootstrap_co = mod.__loader__.get_code(mod_name)
        except Exception:
            bootstrap_co = None

        if bootstrap_co:
            exec(bootstrap_co)
            sys.exit(0)

        # Load from file; requires pyqtgraph/multiprocess/bootstrap.py collected as data file
        bootstrap_file = os.path.join(sys._MEIPASS, 'pyqtgraph', 'multiprocess', 'bootstrap.py')
        if os.path.isfile(bootstrap_file):
            with open(bootstrap_file, 'r') as fp:
                bootstrap_code = fp.read()
            exec(bootstrap_code)
            sys.exit(0)

        raise RuntimeError("Could not find pyqtgraph.multiprocess bootstrap code or script!")


_setup_pyqtgraph_multiprocess_hook()
del _setup_pyqtgraph_multiprocess_hook
