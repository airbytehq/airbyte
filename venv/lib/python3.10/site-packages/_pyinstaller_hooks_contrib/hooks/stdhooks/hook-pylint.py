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
# *************************************************
# hook-pylint.py - PyInstaller hook file for pylint
# *************************************************
# The pylint package, in __pkginfo__.py, is version 1.4.3. Looking at its
# source:
#
# From checkers/__init__.py, starting at line 122::
#
#    def initialize(linter):
#        """initialize linter with checkers in this package """
#        register_plugins(linter, __path__[0])
#
# From reporters/__init__.py, starting at line 131::
#
#    def initialize(linter):
#        """initialize linter with reporters in this package """
#        utils.register_plugins(linter, __path__[0])
#
# From utils.py, starting at line 881::
#
#    def register_plugins(linter, directory):
#        """load all module and package in the given directory, looking for a
#        'register' function in each one, used to register pylint checkers
#        """
#        imported = {}
#        for filename in os.listdir(directory):
#            base, extension = splitext(filename)
#            if base in imported or base == '__pycache__':
#                continue
#            if extension in PY_EXTS and base != '__init__' or (
#                 not extension and isdir(join(directory, base))):
#                try:
#                    module = load_module_from_file(join(directory, filename))
#
#
# So, we need all the Python source in the ``checkers/`` and ``reporters/``
# subdirectories, since these are run-time discovered and loaded. Therefore,
# these files are all data files. In addition, since this is a module, the
# pylint/__init__.py file must be included, since submodules must be children of
# a module.

from PyInstaller.utils.hooks import (
    collect_data_files, collect_submodules, is_module_or_submodule, get_module_file_attribute
)

datas = (
    [(get_module_file_attribute('pylint.__init__'), 'pylint')] +
    collect_data_files('pylint.checkers', True) +
    collect_data_files('pylint.reporters', True)
)


# Add imports from dynamically loaded modules, excluding pylint.test
# subpackage (pylint <= 2.3) and pylint.testutils submodule (pylint < 2.7)
# or subpackage (pylint >= 2.7)
def _filter_func(name):
    return (
        not is_module_or_submodule(name, 'pylint.test') and
        not is_module_or_submodule(name, 'pylint.testutils')
    )


hiddenimports = collect_submodules('pylint', _filter_func)
