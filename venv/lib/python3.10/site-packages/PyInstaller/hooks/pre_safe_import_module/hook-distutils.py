#-----------------------------------------------------------------------------
# Copyright (c) 2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller import compat
from PyInstaller.utils import hooks as hookutils


def pre_safe_import_module(api):
    # `distutils` was removed from from stdlib in python 3.12; if it is available, it is provided by `setuptools`.
    # Therefore, we need to mark it as a run-time package - this ensures that even though modulegraph cannot find the
    # module, it will call the standard hook nevertheless, and the standard hook will trigger the collection of
    # `setuptools`, which in turn will make `distutils` available at the run-time.
    #
    # Unfortunately, making the package a run-time package also means that we need to mark all its submodules and
    # subpackages as run-time ones as well...
    if compat.is_py312:
        distutils_submodules = hookutils.collect_submodules('setuptools._distutils')

        # Known package names - so we can avoid calling hooksutils.is_package() for every entry...
        PACKAGES = {'distutils', 'distutils.command'}

        for module_name in distutils_submodules:
            mapped_name = module_name.replace('setuptools._distutils', 'distutils')
            if mapped_name in PACKAGES:
                api.add_runtime_package(mapped_name)
            else:
                api.add_runtime_module(mapped_name)
