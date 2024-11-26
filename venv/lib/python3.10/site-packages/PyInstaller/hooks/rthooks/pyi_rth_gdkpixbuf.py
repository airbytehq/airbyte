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
    import atexit
    import os
    import sys
    import tempfile

    pixbuf_file = os.path.join(sys._MEIPASS, 'lib', 'gdk-pixbuf', 'loaders.cache')

    # If we are not on Windows, we need to rewrite the cache -> we rewrite on Mac OS to support --onefile mode
    if os.path.exists(pixbuf_file) and sys.platform != 'win32':
        with open(pixbuf_file, 'rb') as fp:
            contents = fp.read()

        # Create a temporary file with the cache and cleverly replace the prefix we injected with the actual path.
        fd, pixbuf_file = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as fp:
            libpath = os.path.join(sys._MEIPASS, 'lib').encode('utf-8')
            fp.write(contents.replace(b'@executable_path/lib', libpath))

        try:
            atexit.register(os.unlink, pixbuf_file)
        except OSError:
            pass

    os.environ['GDK_PIXBUF_MODULE_FILE'] = pixbuf_file


_pyi_rthook()
del _pyi_rthook
