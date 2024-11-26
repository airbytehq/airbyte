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

msg = """
=============================================================
A RecursionError (maximum recursion depth exceeded) occurred.
For working around please follow these instructions
=============================================================

1. In your program's .spec file add this line near the top::

     import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

2. Build your program by running PyInstaller with the .spec file as
   argument::

     pyinstaller myprog.spec

3. If this fails, you most probably hit an endless recursion in
   PyInstaller. Please try to track this down has far as possible,
   create a minimal example so we can reproduce and open an issue at
   https://github.com/pyinstaller/pyinstaller/issues following the
   instructions in the issue template. Many thanks.

Explanation: Python's stack-limit is a safety-belt against endless recursion,
eating up memory. PyInstaller imports modules recursively. If the structure
how modules are imported within your program is awkward, this leads to the
nesting being too deep and hitting Python's stack-limit.

With the default recursion limit (1000), the recursion error occurs at about
115 nested imported, with limit 2000 at about 240, with limit 5000 at about
660.
"""


def raise_with_msg():
    raise SystemExit(msg)
