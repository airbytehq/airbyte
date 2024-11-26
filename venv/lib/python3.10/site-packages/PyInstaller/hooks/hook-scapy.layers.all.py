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

from PyInstaller.utils.hooks import collect_submodules

# The layers to load can be configured using scapy's conf.load_layers.
#  from scapy.config import conf; print(conf.load_layers)
# I decided not to use this, but to include all layer modules. The reason is: When building the package, load_layers may
# not include all the layer modules the program will use later.

hiddenimports = collect_submodules('scapy.layers')
