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

from PyInstaller.utils.hooks import collect_submodules, check_requirement, can_import_module

# pkg_resources keeps vendored modules in its _vendor subpackage, and does sys.meta_path based import magic to expose
# them as pkg_resources.extern.*

# The `railroad` package is an optional requirement for `pyparsing`. `pyparsing.diagrams` depends on `railroad`, so
# filter it out when `railroad` is not available.
if can_import_module('railroad'):
    hiddenimports = collect_submodules('pkg_resources._vendor')
else:
    hiddenimports = collect_submodules(
        'pkg_resources._vendor', filter=lambda name: 'pkg_resources._vendor.pyparsing.diagram' not in name
    )

# pkg_resources v45.0 dropped support for Python 2 and added this module printing a warning. We could save some bytes if
# we would replace this by a fake module.
if check_requirement('setuptools >= 45.0.0, < 49.1.1'):
    hiddenimports.append('pkg_resources.py2_warn')

excludedimports = ['__main__']

# Some more hidden imports. See:
# https://github.com/pyinstaller/pyinstaller-hooks-contrib/issues/15#issuecomment-663699288 `packaging` can either be
# its own package, or embedded in `pkg_resources._vendor.packaging`, or both.
hiddenimports += collect_submodules('packaging')

# As of v60.7, setuptools vendored jaraco and has pkg_resources use it. Currently, the pkg_resources._vendor.jaraco
# namespace package cannot be automatically scanned due to limited support for pure namespace packages in our hook
# utilities.
#
# In setuptools 60.7.0, the vendored jaraco.text package included "Lorem Ipsum.txt" data file, which also has to be
# collected. However, the presence of the data file (and the resulting directory hierarchy) confuses the importer's
# redirection logic; instead of trying to work-around that, tell user to upgrade or downgrade their setuptools.
if check_requirement("setuptools == 60.7.0"):
    raise SystemExit(
        "ERROR: Setuptools 60.7.0 is incompatible with PyInstaller. "
        "Downgrade to an earlier version or upgrade to a later version."
    )
# In setuptools 60.7.1, the "Lorem Ipsum.txt" data file was dropped from the vendored jaraco.text package, so we can
# accommodate it with couple of hidden imports.
elif check_requirement("setuptools >= 60.7.1"):
    hiddenimports += [
        'pkg_resources._vendor.jaraco.functools',
        'pkg_resources._vendor.jaraco.context',
        'pkg_resources._vendor.jaraco.text',
    ]
