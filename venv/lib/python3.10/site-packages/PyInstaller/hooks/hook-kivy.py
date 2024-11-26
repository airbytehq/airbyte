#-----------------------------------------------------------------------------
# Copyright (c) 2015-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller import log as logging
from PyInstaller.utils.hooks import check_requirement

if check_requirement('kivy >= 1.9.1'):
    from kivy.tools.packaging.pyinstaller_hooks import (add_dep_paths, get_deps_all, get_factory_modules, kivy_modules)
    from kivy.tools.packaging.pyinstaller_hooks import excludedimports, datas  # noqa: F401

    add_dep_paths()

    hiddenimports = get_deps_all()['hiddenimports']
    hiddenimports = list(set(get_factory_modules() + kivy_modules + hiddenimports))
else:
    logger = logging.getLogger(__name__)
    logger.warning('Hook disabled because of Kivy version < 1.9.1')
