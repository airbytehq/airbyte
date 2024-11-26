# -----------------------------------------------------------------------------
# Copyright (c) 2021-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) or, at the user's discretion, the MIT License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception OR MIT)
# -----------------------------------------------------------------------------
"""
PyInstaller hooks typically will need to import the package which they are written for but doing so may manipulate
globals such as :data:`sys.path` or :data:`os.environ` in ways that affect the build. For example, on Windows,
Qt's binaries are added to then loaded via ``PATH`` in such a way that if you import multiple Qt variants in one
session then there is no guarantee which variant's binaries each variant will get!

To get around this, PyInstaller does any such tasks in an isolated Python subprocess and ships a
:mod:`PyInstaller.isolated` submodule to do so in hooks. ::

    from PyInstaller import isolated

This submodule provides:

*   :func:`isolated.call() <call>` to evaluate functions in isolation.
*   :func:`@isolated.decorate <decorate>` to mark a function as always called in isolation.
*   :class:`isolated.Python() <Python>` to efficiently call many functions in a single child instance of Python.

"""

# ruff: noqa
from ._parent import Python, call, decorate
