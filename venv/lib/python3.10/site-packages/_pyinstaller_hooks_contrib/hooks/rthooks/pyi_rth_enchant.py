#-----------------------------------------------------------------------------
# Copyright (c) 2005-2020, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

import os
import sys

# On Mac OS X tell enchant library where to look for enchant backends (aspell, myspell, ...).
# Enchant is looking for backends in directory 'PREFIX/lib/enchant'
# Note: env. var. ENCHANT_PREFIX_DIR is implemented only in the development version:
#    https://github.com/AbiWord/enchant
#    https://github.com/AbiWord/enchant/pull/2
# TODO Test this rthook.
if sys.platform.startswith('darwin'):
    os.environ['ENCHANT_PREFIX_DIR'] = os.path.join(sys._MEIPASS, 'enchant')
