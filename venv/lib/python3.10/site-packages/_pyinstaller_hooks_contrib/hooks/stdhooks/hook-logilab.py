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
#
# ***************************************************
# hook-logilab.py - PyInstaller hook file for logilab
# ***************************************************
# The following was written about logilab, version 1.1.0, based on executing
# ``pip show logilab-common``.
#
# In logilab.common, line 33::
#
#    __version__ = pkg_resources.get_distribution('logilab-common').version
#
# Therefore, we need metadata for logilab.
from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('logilab-common')
