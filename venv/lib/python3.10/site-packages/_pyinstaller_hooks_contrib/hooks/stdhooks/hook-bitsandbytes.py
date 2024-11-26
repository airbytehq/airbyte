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
# ---------------------------------------------------

from PyInstaller.utils.hooks import collect_dynamic_libs

# bitsandbytes contains several extensions for CPU and different CUDA versions: libbitsandbytes_cpu.so,
# libbitsandbytes_cuda110_nocublaslt.so, libbitsandbytes_cuda110.so, etc. At build-time, we could query the
# `bitsandbytes.cextension.setup` and its `binary_name˙ attribute for the extension that is in use. However, if the
# build system does not have CUDA available, this would automatically mean that we will not collect any of the CUDA
# libs. So for now, we collect them all.
binaries = collect_dynamic_libs("bitsandbytes")

# bitsandbytes uses triton's JIT module, which requires access to source .py files.
module_collection_mode = 'pyz+py'
