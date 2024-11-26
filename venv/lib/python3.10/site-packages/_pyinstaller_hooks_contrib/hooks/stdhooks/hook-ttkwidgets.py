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
Hook for use with the ttkwidgets package

ttkwidgets provides a set of cross-platform widgets for Tkinter/ttk,
some of which depend on image files in order to function properly.

These images files are all provided in the `ttkwidgets/assets` folder,
which has to be copied by PyInstaller.

This hook has been tested on Ubuntu 18.04 (Python 3.6.8 venv) and
Windows 7 (Python 3.5.4 system-wide).

>>> import tkinter as tk
>>> from ttkwidgets import CheckboxTreeview
>>>
>>> window = tk.Tk()
>>> tree = CheckboxTreeview(window)
>>> tree.insert("", tk.END, "test", text="Hello World!")
>>> tree.insert("test", tk.END, "test2", text="Hello World again!")
>>> tree.insert("test", tk.END, "test3", text="Hello World again again!")
>>> tree.pack()
>>> window.mainloop()
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("ttkwidgets")
