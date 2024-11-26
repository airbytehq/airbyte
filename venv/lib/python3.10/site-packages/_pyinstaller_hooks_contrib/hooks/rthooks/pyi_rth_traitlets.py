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

# 'traitlets' uses module 'inspect' from default Python library to inspect
# source code of modules. However, frozen app does not contain source code
# of Python modules.
#
# hook-IPython depends on module 'traitlets'.

import traitlets.traitlets


def _disabled_deprecation_warnings(method, cls, method_name, msg):
    pass


traitlets.traitlets._deprecated_method = _disabled_deprecation_warnings
