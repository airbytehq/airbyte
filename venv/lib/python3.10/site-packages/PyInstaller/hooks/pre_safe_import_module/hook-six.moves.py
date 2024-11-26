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


def pre_safe_import_module(api):
    """
    Add the `six.moves` module as a dynamically defined runtime module node and all modules mapped by
    `six._SixMetaPathImporter` as aliased module nodes to the passed graph.

    The `six.moves` module is dynamically defined at runtime by the `six` module and hence cannot be imported in the
    standard way. Instead, this hook adds a placeholder node for the `six.moves` module to the graph,
    which implicitly adds an edge from that node to the node for its parent `six` module. This ensures that the `six`
    module will be frozen into the executable. (Phew!)

    `six._SixMetaPathImporter` is a PEP 302-compliant module importer converting imports independent of the current
    Python version into imports specific to that version (e.g., under Python 3, from `from six.moves import
    tkinter_tix` to `import tkinter.tix`). For each such mapping, this hook adds a corresponding module alias to the
    graph allowing PyInstaller to translate the former to the latter.
    """
    @isolated.call
    def real_to_six_module_name():
        """
        Generate a dictionary from conventional module names to "six.moves" attribute names (e.g., from `tkinter.tix` to
        `six.moves.tkinter_tix`).
        """
        try:
            import six
        except ImportError:
            return None  # unavailable

        # Iterate over the "six._moved_attributes" list rather than the "six._importer.known_modules" dictionary, as
        # "urllib"-specific moved modules are overwritten in the latter with unhelpful "LazyModule" objects. If this is
        # a moved module or attribute, map the corresponding module. In the case of moved attributes, the attribute's
        # module is mapped while the attribute itself is mapped at runtime and hence ignored here.
        return {
            moved.mod: 'six.moves.' + moved.name
            for moved in six._moved_attributes if isinstance(moved, (six.MovedModule, six.MovedAttribute))
        }

    # Add "six.moves" as a runtime package rather than module. Modules cannot physically contain submodules; only
    # packages can. In "from"-style import statements (e.g., "from six.moves import queue"), this implies that:
    # * Attributes imported from customary modules are guaranteed *NOT* to be submodules. Hence, ModuleGraph justifiably
    #   ignores these attributes. While some attributes declared by "six.moves" are ignorable non-modules (e.g.,
    #   functions, classes), others are non-ignorable submodules that must be imported. Adding "six.moves" as a runtime
    #   module causes ModuleGraph to ignore these submodules, which defeats the entire point.
    # * Attributes imported from packages could be submodules. To disambiguate non-ignorable submodules from ignorable
    #   non-submodules (e.g., classes, variables), ModuleGraph first attempts to import these attributes as submodules.
    #   This is exactly what we want.
    if real_to_six_module_name is not None:
        api.add_runtime_package(api.module_name)
        for real_module_name, six_module_name in real_to_six_module_name.items():
            api.add_alias_module(real_module_name, six_module_name)
