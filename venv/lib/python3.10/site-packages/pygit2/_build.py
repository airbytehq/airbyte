# Copyright 2010-2023 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

"""
This is an special module, it provides stuff used by setup.py at build time.
But also used by pygit2 at run time.
"""

import os
from pathlib import Path

#
# The version number of pygit2
#
__version__ = '1.13.3'


#
# Utility functions to get the paths required for bulding extensions
#
def _get_libgit2_path():
    # LIBGIT2 environment variable takes precedence
    libgit2_path = os.getenv('LIBGIT2')
    if libgit2_path is not None:
        return Path(libgit2_path)

    # Default
    if os.name == 'nt':
        return Path(r'%s\libgit2' % os.getenv('ProgramFiles'))
    return Path('/usr/local')


def get_libgit2_paths():
    # Base path
    path = _get_libgit2_path()

    # Library dirs
    libgit2_lib = os.getenv('LIBGIT2_LIB')
    if libgit2_lib is None:
        library_dirs = [path / 'lib', path / 'lib64']
    else:
        library_dirs = [libgit2_lib]

    include_dirs = [path / 'include']
    return (
        path / 'bin',
        {
            'libraries': ['git2'],
            'include_dirs': [str(x) for x in include_dirs],
            'library_dirs': [str(x) for x in library_dirs],
        }
    )
