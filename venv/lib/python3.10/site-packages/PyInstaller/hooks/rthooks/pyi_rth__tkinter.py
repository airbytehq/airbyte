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


def _pyi_rthook():
    import os
    import sys

    tcldir = os.path.join(sys._MEIPASS, 'tcl')
    tkdir = os.path.join(sys._MEIPASS, 'tk')

    # Notify "tkinter" of data directories. On macOS, we do not collect data directories if system Tcl/Tk framework is
    # used. On other OSes, we always collect them, so their absence is considered an error.
    is_darwin = sys.platform == 'darwin'

    if os.path.isdir(tcldir):
        os.environ["TCL_LIBRARY"] = tcldir
    elif not is_darwin:
        raise FileNotFoundError('Tcl data directory "%s" not found.' % tcldir)

    if os.path.isdir(tkdir):
        os.environ["TK_LIBRARY"] = tkdir
    elif not is_darwin:
        raise FileNotFoundError('Tk data directory "%s" not found.' % tkdir)


_pyi_rthook()
del _pyi_rthook
