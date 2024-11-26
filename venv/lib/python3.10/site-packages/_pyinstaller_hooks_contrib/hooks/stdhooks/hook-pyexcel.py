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

# This hook was tested with pyexcel 0.5.13:
# https://github.com/pyexcel/pyexcel

hiddenimports = [
    'pyexcel.plugins.renderers.sqlalchemy', 'pyexcel.plugins.renderers.django',
    'pyexcel.plugins.renderers.excel', 'pyexcel.plugins.renderers._texttable',
    'pyexcel.plugins.parsers.excel', 'pyexcel.plugins.parsers.sqlalchemy',
    'pyexcel.plugins.sources.http', 'pyexcel.plugins.sources.file_input',
    'pyexcel.plugins.sources.memory_input',
    'pyexcel.plugins.sources.file_output',
    'pyexcel.plugins.sources.output_to_memory',
    'pyexcel.plugins.sources.pydata.bookdict',
    'pyexcel.plugins.sources.pydata.dictsource',
    'pyexcel.plugins.sources.pydata.arraysource',
    'pyexcel.plugins.sources.pydata.records', 'pyexcel.plugins.sources.django',
    'pyexcel.plugins.sources.sqlalchemy', 'pyexcel.plugins.sources.querysets'
]
