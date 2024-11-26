#-----------------------------------------------------------------------------
# Copyright (c) 2015-2020, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

import os
import sys

# Installing `pyproj` Conda packages requires to set `PROJ_LIB`

is_win = sys.platform.startswith('win')
if is_win:

    proj_data = os.path.join(sys._MEIPASS, 'Library', 'share', 'proj')

else:
    proj_data = os.path.join(sys._MEIPASS, 'share', 'proj')

if os.path.exists(proj_data):
    os.environ['PROJ_LIB'] = proj_data
