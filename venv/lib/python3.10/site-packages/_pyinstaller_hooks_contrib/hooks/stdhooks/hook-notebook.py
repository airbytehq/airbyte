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

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from jupyter_core.paths import jupyter_config_path, jupyter_path

# collect modules for handlers
hiddenimports = collect_submodules('notebook', filter=lambda name: name.endswith('.handles'))
hiddenimports.append('notebook.services.shutdown')

datas = collect_data_files('notebook')

# Collect share and etc folder for pre-installed extensions
datas += [(path, 'share/jupyter')
          for path in jupyter_path() if os.path.exists(path)]
datas += [(path, 'etc/jupyter')
          for path in jupyter_config_path() if os.path.exists(path)]
