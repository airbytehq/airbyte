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

from PyInstaller import isolated

# This is basically a copy of pre_safe_import_module/hook-six.moves.py adopted to setuptools.extern.six resp.
# setuptools._vendor.six. Please see pre_safe_import_module/hook-six.moves.py for documentation.

# Note that the moves are defined in 'setuptools._vendor.six' but are imported under 'setuptools.extern.six'.


def pre_safe_import_module(api):
    @isolated.call
    def real_to_six_module_name():
        try:
            import setuptools._vendor.six as six
        except ImportError:
            try:
                import setuptools.extern.six as six
            except ImportError:
                return None  # unavailable

        return {
            moved.mod: 'setuptools.extern.six.moves.' + moved.name
            for moved in six._moved_attributes if isinstance(moved, (six.MovedModule, six.MovedAttribute))
        }

    if real_to_six_module_name is not None:
        api.add_runtime_package(api.module_name)
        for real_module_name, six_module_name in real_to_six_module_name.items():
            api.add_alias_module(real_module_name, six_module_name)
