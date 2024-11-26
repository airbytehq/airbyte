# ------------------------------------------------------------------
# Copyright (c) 2023 PyInstaller Development Team.
#
# This file is distributed under the terms of the Apache License 2.0
#
# The full license is available in LICENSE.APL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: Apache-2.0
# ------------------------------------------------------------------

# `moviepy.video.fx.all` programmatically imports and forwards all submodules of `moviepy.video.fx`, so we need to
# collect those as hidden imports.
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('moviepy.video.fx')
