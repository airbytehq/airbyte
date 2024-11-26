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

    # Without this environment variable set to 'no' importing 'gst' causes 100% CPU load. (Tested on Mac OS.)
    os.environ['GST_REGISTRY_FORK'] = 'no'

    gst_plugin_paths = [sys._MEIPASS, os.path.join(sys._MEIPASS, 'gst-plugins')]
    os.environ['GST_PLUGIN_PATH'] = os.pathsep.join(gst_plugin_paths)

    # Prevent permission issues on Windows
    os.environ['GST_REGISTRY'] = os.path.join(sys._MEIPASS, 'registry.bin')

    # Only use packaged plugins to prevent GStreamer from crashing when it finds plugins from another version which are
    # installed system wide.
    os.environ['GST_PLUGIN_SYSTEM_PATH'] = ''


_pyi_rthook()
del _pyi_rthook
