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
"""
Hook for Python bindings for Amazon's Product Advertising API.
https://bitbucket.org/basti/python-amazon-product-api
"""

hiddenimports = ['amazonproduct.processors.__init__',
                 'amazonproduct.processors._lxml',
                 'amazonproduct.processors.objectify',
                 'amazonproduct.processors.elementtree',
                 'amazonproduct.processors.etree',
                 'amazonproduct.processors.minidom',
                 'amazonproduct.contrib.__init__',
                 'amazonproduct.contrib.cart',
                 'amazonproduct.contrib.caching',
                 'amazonproduct.contrib.retry']
