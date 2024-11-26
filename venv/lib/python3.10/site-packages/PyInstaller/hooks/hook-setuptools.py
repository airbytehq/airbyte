#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.compat import is_darwin, is_unix
from PyInstaller.utils.hooks import collect_submodules, check_requirement

hiddenimports = [
    # Test case import/test_zipimport2 fails during importing pkg_resources or setuptools when module not present.
    'distutils.command.build_ext',
    'setuptools.msvc',
]

# Necessary for setuptools on Mac/Unix
if is_unix or is_darwin:
    hiddenimports.append('syslog')

# setuptools >= 39.0.0 is "vendoring" its own direct dependencies from "_vendor" to "extern". This also requires
# 'pre_safe_import_module/hook-setuptools.extern.six.moves.py' to make the moves defined in 'setuptools._vendor.six'
# importable under 'setuptools.extern.six'.
_excluded_submodules = (
    # Prevent recursing into setuptools._vendor.pyparsing.diagram, which typically fails to be imported due to
    # missing dependencies (railroad, pyparsing (?), jinja2) and generates a warning... As the module is usually
    # unimportable, it is likely not to be used by setuptools.
    'setuptools._vendor.pyparsing.diagram',
)
hiddenimports.extend(collect_submodules('setuptools._vendor', filter=lambda name: name not in _excluded_submodules))

# As of setuptools >= 60.0, we need to collect the vendored version of distutils via hiddenimports. The corresponding
# pyi_rth_setuptools runtime hook ensures that the _distutils_hack is installed at the program startup, which allows
# setuptools to override the stdlib distutils with its vendored version, if necessary.
if check_requirement("setuptools >= 60.0"):
    hiddenimports += ["_distutils_hack"]
    hiddenimports += collect_submodules("setuptools._distutils")
