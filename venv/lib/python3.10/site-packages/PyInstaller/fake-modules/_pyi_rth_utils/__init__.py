# -----------------------------------------------------------------------------
# Copyright (c) 2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
# -----------------------------------------------------------------------------

import sys

# A boolean indicating whether the frozen application is a macOS .app bundle.
is_macos_app_bundle = sys.platform == 'darwin' and sys._MEIPASS.endswith("Contents/Frameworks")
