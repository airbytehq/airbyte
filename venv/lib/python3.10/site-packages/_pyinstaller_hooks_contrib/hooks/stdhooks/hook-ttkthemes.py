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
"""
Hook for use with the ttkthemes package

ttkthemes depends on a large set of image and Tcl-code files contained
within its package directory. These are not imported, and thus this hook
is required so they are copied.

The file structure of the ttkthemes package folder is:
ttkthemes
├───advanced
|   └───*.tcl
├───themes
|   ├───theme1
|   |   ├───theme1
|   |   |   └───*.gif
|   |   └───theme1.tcl
|   ├───theme2
|   ├───...
|   └───pkgIndex.tcl
├───png
└───gif

The ``themes`` directory contains themes which only have a universal
image version (either base64 encoded in the theme files or GIF), while
``png`` and ``gif`` contain the PNG and GIF versions of the themes which
support both respectively.

All of this must be copied, as the package expects all the data to be
present and only checks what themes to load at runtime.

Tested hook on Linux (Ubuntu 18.04, Python 3.6 minimal venv) and on
Windows 7 (Python 3.7, minimal system-wide installation).

>>> from tkinter import ttk
>>> from ttkthemes import ThemedTk
>>>
>>>
>>> if __name__ == '__main__':
>>>     window = ThemedTk(theme="plastik")
>>>     ttk.Button(window, text="Quit", command=window.destroy).pack()
>>>     window.mainloop()
"""
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("ttkthemes")
