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

# This hook was tested with pyexcel-io 0.5.18:
# https://github.com/pyexcel/pyexcel-io

hiddenimports = [
    'pyexcel_io.readers.csvr', 'pyexcel_io.readers.csvz',
    'pyexcel_io.readers.tsv', 'pyexcel_io.readers.tsvz',
    'pyexcel_io.writers.csvw', 'pyexcel_io.writers.csvz',
    'pyexcel_io.writers.tsv', 'pyexcel_io.writers.tsvz',
    'pyexcel_io.readers.csvz', 'pyexcel_io.readers.tsv',
    'pyexcel_io.readers.tsvz', 'pyexcel_io.database.importers.django',
    'pyexcel_io.database.importers.sqlalchemy',
    'pyexcel_io.database.exporters.django',
    'pyexcel_io.database.exporters.sqlalchemy'
]
