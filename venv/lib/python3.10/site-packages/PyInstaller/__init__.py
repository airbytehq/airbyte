#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

__all__ = ('HOMEPATH', 'PLATFORM', '__version__', 'DEFAULT_DISTPATH', 'DEFAULT_SPECPATH', 'DEFAULT_WORKPATH')

import os
import sys

from PyInstaller import compat
from PyInstaller.utils.git import get_repo_revision

# Note: Keep this variable as plain string so it could be updated automatically when doing a release.
__version__ = '6.3.0'

# Absolute path of this package's directory. Save this early so all submodules can use the absolute path. This is
# required for example if the current directory changes prior to loading the hooks.
PACKAGEPATH = os.path.abspath(os.path.dirname(__file__))

HOMEPATH = os.path.dirname(PACKAGEPATH)

# Update __version__ as necessary.
if os.path.exists(os.path.join(HOMEPATH, 'setup.py')):
    # PyInstaller is run directly from source without installation, or __version__ is called from 'setup.py'...
    if compat.getenv('PYINSTALLER_DO_RELEASE') == '1':
        # Suppress the git revision when doing a release.
        pass
    elif 'sdist' not in sys.argv:
        # and 'setup.py' was not called with 'sdist' argument. For creating source tarball we do not want git revision
        # in the filename.
        try:
            __version__ += get_repo_revision()
        except Exception:
            # Write to stderr because stdout is used for eval() statement in some subprocesses.
            sys.stderr.write('WARN: failed to parse git revision')
else:
    # PyInstaller was installed by `python setup.py install'.
    from importlib.metadata import version
    __version__ = version('PyInstaller')
# Default values of paths where to put files created by PyInstaller. If changing these, do not forget to update the
# help text for corresponding command-line options, defined in build_main.

# Where to put created .spec file.
DEFAULT_SPECPATH = os.getcwd()
# Where to put the final frozen application.
DEFAULT_DISTPATH = os.path.join(os.getcwd(), 'dist')
# Where to put all the temporary files; .log, .pyz, etc.
DEFAULT_WORKPATH = os.path.join(os.getcwd(), 'build')

PLATFORM = compat.system + '-' + compat.architecture
# Include machine name in path to bootloader for some machines (e.g., 'arm'). Explicitly avoid doing this on macOS,
# where we keep universal2 bootloaders in Darwin-64bit folder regardless of whether we are on x86_64 or arm64.
if compat.machine and not compat.is_darwin:
    PLATFORM += '-' + compat.machine
# Similarly, disambiguate musl Linux from glibc Linux.
if compat.is_musl:
    PLATFORM += '-musl'
