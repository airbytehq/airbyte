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

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, eval_statement

# Sphinx consists of several extensions that are lazily loaded. So collect all submodules to ensure we do not miss
# any of them.
hiddenimports = collect_submodules('sphinx')

# For each extension in sphinx.application.builtin_extensions that does not come from the sphinx package, do a
# collect_submodules(). We need to do this explicitly because collect_submodules() does not seem to work with
# namespace packages, which precludes us from simply doing hiddenimports += collect_submodules('sphinxcontrib')
builtin_extensions = list(
    eval_statement(
        """
        from sphinx.application import builtin_extensions
        print(builtin_extensions)
        """
    )
)
for extension in builtin_extensions:
    if extension.startswith('sphinx.'):
        continue  # Already collected
    hiddenimports += collect_submodules(extension)

# This is inherited from an earlier version of the hook, and seems to have been required in Sphinx v.1.3.1 era due to
# https://github.com/sphinx-doc/sphinx/blob/b87ce32e7dc09773f9e71305e66e8d6aead53dd1/sphinx/cmdline.py#L173.
# It does not hurt to keep it around, just in case.
hiddenimports += ['locale']

# Collect all data files: *.html and *.conf files in ``sphinx.themes``, translation files in ``sphinx.locale``, etc.
# Also collect all data files for the alabaster theme.
datas = collect_data_files('sphinx') + collect_data_files('alabaster')
