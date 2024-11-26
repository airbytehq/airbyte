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

import os
import sys
import errno
import tempfile

# Helper for creating temporary directories with access restricted to the user running the process.
# On POSIX systems, this is already achieved by `tempfile.mkdtemp`, which uses 0o700 permissions mask.
# On Windows, however, the POSIX permissions semantics have no effect, and we need to provide our own implementation
# that restricts the access by passing appropriate security attributes to the `CreateDirectory` function.

if os.name == 'nt':
    from . import _win32

    def secure_mkdtemp(suffix=None, prefix=None, dir=None):
        """
        Windows-specific replacement for `tempfile.mkdtemp` that restricts access to the user running the process.
        Based on `mkdtemp` implementation from python 3.11 stdlib.
        """

        prefix, suffix, dir, output_type = tempfile._sanitize_params(prefix, suffix, dir)

        names = tempfile._get_candidate_names()
        if output_type is bytes:
            names = map(os.fsencode, names)

        for seq in range(tempfile.TMP_MAX):
            name = next(names)
            file = os.path.join(dir, prefix + name + suffix)
            sys.audit("tempfile.mkdtemp", file)
            try:
                _win32.secure_mkdir(file)
            except FileExistsError:
                continue  # try again
            except PermissionError:
                # This exception is thrown when a directory with the chosen name already exists on windows.
                if (os.name == 'nt' and os.path.isdir(dir) and os.access(dir, os.W_OK)):
                    continue
                else:
                    raise
            return file

        raise FileExistsError(errno.EEXIST, "No usable temporary directory name found")

else:
    secure_mkdtemp = tempfile.mkdtemp
