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

# GStreamer contains a lot of plugins. We need to collect them and bundle
# them wih the exe file.
# We also need to resolve binary dependencies of these GStreamer plugins.

import glob
import os
from PyInstaller.compat import is_win
from PyInstaller.utils.hooks import exec_statement

hiddenimports = ['gmodule', 'gobject']

statement = """
import os
import gst
reg = gst.registry_get_default()
plug = reg.find_plugin('coreelements')
path = plug.get_filename()
print(os.path.dirname(path))
"""

plugin_path = exec_statement(statement)

if is_win:
    # TODO Verify that on Windows gst plugins really end with .dll.
    pattern = os.path.join(plugin_path, '*.dll')
else:
    # Even on OSX plugins end with '.so'.
    pattern = os.path.join(plugin_path, '*.so')

binaries = [
    (os.path.join('gst_plugins', os.path.basename(f)), f)
    # 'f' contains the absolute path
    for f in glob.glob(pattern)]
