#-----------------------------------------------------------------------------
# Copyright (c) 2021, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

import pygraphviz

# Override pygraphviz.AGraph._which method to search for graphviz executables inside sys._MEIPASS
if hasattr(pygraphviz.AGraph, '_which'):

    def _pygraphviz_override_which(self, name):
        import os
        import sys
        import platform

        program_name = name
        if platform.system() == "Windows":
            program_name += ".exe"

        program_path = os.path.join(sys._MEIPASS, program_name)
        if not os.path.isfile(program_path):
            raise ValueError(f"Prog {name} not found in the PyInstaller-frozen application bundle!")

        return program_path

    pygraphviz.AGraph._which = _pygraphviz_override_which
