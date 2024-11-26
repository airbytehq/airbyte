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

import os
if os.name == 'posix':
    hiddenimports = [
        'libvtkCommonPython', 'libvtkFilteringPython', 'libvtkIOPython',
        'libvtkImagingPython', 'libvtkGraphicsPython', 'libvtkRenderingPython',
        'libvtkHybridPython', 'libvtkParallelPython', 'libvtkPatentedPython'
    ]
else:
    hiddenimports = [
        'vtkCommonPython', 'vtkFilteringPython', 'vtkIOPython',
        'vtkImagingPython', 'vtkGraphicsPython', 'vtkRenderingPython',
        'vtkHybridPython', 'vtkParallelPython', 'vtkPatentedPython'
    ]
