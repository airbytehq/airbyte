#-----------------------------------------------------------------------------
# Copyright (c) 2021-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------


def _pyi_rthook():
    import inspect
    import os
    import sys

    _orig_inspect_getsourcefile = inspect.getsourcefile

    # Provide custom implementation of inspect.getsourcefile() for frozen applications that properly resolves relative
    # filenames obtained from object (e.g., inspect stack-frames). See #5963.
    def _pyi_getsourcefile(object):
        filename = inspect.getfile(object)
        if not os.path.isabs(filename):
            # Check if given filename matches the basename of __main__'s __file__.
            main_file = getattr(sys.modules['__main__'], '__file__', None)
            if main_file and filename == os.path.basename(main_file):
                return main_file

            # If filename ends with .py suffix and does not correspond to frozen entry-point script, convert it to
            # corresponding .pyc in sys._MEIPASS.
            if filename.endswith('.py'):
                filename = os.path.normpath(os.path.join(sys._MEIPASS, filename + 'c'))
                # Ensure the relative path did not try to jump out of sys._MEIPASS, just in case...
                if filename.startswith(sys._MEIPASS):
                    return filename
        elif filename.startswith(sys._MEIPASS) and filename.endswith('.pyc'):
            # If filename is already PyInstaller-compatible, prevent any further processing (i.e., with original
            # implementation).
            return filename
        # Use original implementation as a fallback.
        return _orig_inspect_getsourcefile(object)

    inspect.getsourcefile = _pyi_getsourcefile


_pyi_rthook()
del _pyi_rthook
