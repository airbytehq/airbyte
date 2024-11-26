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

    root = os.path.join(sys._MEIPASS, 'kivy_install')

    os.environ['KIVY_DATA_DIR'] = os.path.join(root, 'data')
    os.environ['KIVY_MODULES_DIR'] = os.path.join(root, 'modules')


_pyi_rthook()
del _pyi_rthook
