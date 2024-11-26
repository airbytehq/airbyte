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

import re
import importlib.util

from PyInstaller import isolated
from PyInstaller.lib.modulegraph.modulegraph import SourceModule
from PyInstaller.utils.hooks import check_requirement, logger

# 'sqlalchemy.testing' causes bundling a lot of unnecessary modules.
excludedimports = ['sqlalchemy.testing']

# Include most common database bindings some database bindings are detected and include some are not. We should
# explicitly include database backends.
hiddenimports = ['pysqlite2', 'MySQLdb', 'psycopg2', 'sqlalchemy.ext.baked']

if check_requirement('sqlalchemy >= 1.4'):
    hiddenimports.append("sqlalchemy.sql.default_comparator")


@isolated.decorate
def _get_dialect_modules(module_name):
    import importlib
    module = importlib.import_module(module_name)
    return [f"{module_name}.{submodule_name}" for submodule_name in module.__all__]


# In SQLAlchemy >= 0.6, the "sqlalchemy.dialects" package provides dialects.
# In SQLAlchemy <= 0.5, the "sqlalchemy.databases" package provides dialects.
if check_requirement('sqlalchemy >= 0.6'):
    hiddenimports += _get_dialect_modules("sqlalchemy.dialects")
else:
    hiddenimports += _get_dialect_modules("sqlalchemy.databases")


def hook(hook_api):
    """
    SQLAlchemy 0.9 introduced the decorator 'util.dependencies'.  This decorator does imports. E.g.:

            @util.dependencies("sqlalchemy.sql.schema")

    This hook scans for included SQLAlchemy modules and then scans those modules for any util.dependencies and marks
    those modules as hidden imports.
    """

    if not check_requirement('sqlalchemy >= 0.9'):
        return

    # this parser is very simplistic but seems to catch all cases as of V1.1
    depend_regex = re.compile(r'@util.dependencies\([\'"](.*?)[\'"]\)')

    hidden_imports_set = set()
    known_imports = set()
    for node in hook_api.module_graph.iter_graph(start=hook_api.module):
        if isinstance(node, SourceModule) and node.identifier.startswith('sqlalchemy.'):
            known_imports.add(node.identifier)

            # Read the source...
            with open(node.filename, 'rb') as f:
                source_code = f.read()
            source_code = importlib.util.decode_source(source_code)

            # ... and scan it
            for match in depend_regex.findall(source_code):
                hidden_imports_set.add(match)

    hidden_imports_set -= known_imports
    if len(hidden_imports_set):
        logger.info("  Found %d sqlalchemy hidden imports", len(hidden_imports_set))
        hook_api.add_imports(*list(hidden_imports_set))
