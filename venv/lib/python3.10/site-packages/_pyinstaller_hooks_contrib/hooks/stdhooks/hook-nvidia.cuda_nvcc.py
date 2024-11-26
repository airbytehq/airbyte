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

from PyInstaller.utils.hooks import collect_data_files
from _pyinstaller_hooks_contrib.hooks.utils.nvidia_cuda import collect_nvidia_cuda_binaries

# Ensures that versioned .so files are collected
binaries = collect_nvidia_cuda_binaries(__file__)

# Collect additional resources:
#  - ptxas executable (which strictly speaking, should be collected as a binary)
#  - nvvm/libdevice/libdevice.10.bc file
#  - C headers; assuming ptxas requires them - if that is not the case, we could filter them out.
datas = collect_data_files('nvidia.cuda_nvcc')
