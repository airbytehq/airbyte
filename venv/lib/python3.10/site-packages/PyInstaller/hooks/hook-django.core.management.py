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

from PyInstaller.utils.hooks import collect_submodules

# Module django.core.management.commands.shell imports IPython, but it introduces many other dependencies that are not
# necessary for a simple django project; ignore the IPython module.
excludedimports = ['IPython', 'matplotlib', 'tkinter']

# Django requires management modules for the script 'manage.py'.
hiddenimports = collect_submodules('django.core.management.commands')
