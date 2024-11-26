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

# Installing `osgeo` Conda packages requires to set `GDAL_DATA`

is_win = sys.platform.startswith('win')
if is_win:

    gdal_data = os.path.join(sys._MEIPASS, 'data', 'gdal')
    if not os.path.exists(gdal_data):

        gdal_data = os.path.join(sys._MEIPASS, 'Library', 'share', 'gdal')
        # last attempt, check if one of the required file is in the generic folder Library/data
        if not os.path.exists(os.path.join(gdal_data, 'gcs.csv')):
            gdal_data = os.path.join(sys._MEIPASS, 'Library', 'data')

else:
    gdal_data = os.path.join(sys._MEIPASS, 'share', 'gdal')

if os.path.exists(gdal_data):
    os.environ['GDAL_DATA'] = gdal_data
