#-----------------------------------------------------------------------------
# Copyright (c) 2005-2020, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
PyWin32 package 'win32com' extends it's __path__ attribute with win32comext
directory and thus PyInstaller is not able to find modules in it. For example
module 'win32com.shell' is in reality 'win32comext.shell'.

>>> win32com.__path__
['win32com', 'C:\\Python27\\Lib\\site-packages\\win32comext']

"""

import os

from PyInstaller.utils.hooks import logger, exec_statement
from PyInstaller.compat import is_win, is_cygwin


def pre_safe_import_module(api):
    if not (is_win or is_cygwin):
        return
    win32com_file = exec_statement(
        """
        try:
            from win32com import __file__
            print(__file__)
        except Exception:
            pass
        """).strip()
    if not win32com_file:
        logger.debug('win32com: module not available')
        return  # win32com unavailable
    win32com_dir = os.path.dirname(win32com_file)
    comext_dir = os.path.join(os.path.dirname(win32com_dir), 'win32comext')
    logger.debug('win32com: extending __path__ with dir %r' % comext_dir)
    # Append the __path__ where PyInstaller will look for 'win32com' modules.'
    api.append_package_path(comext_dir)
