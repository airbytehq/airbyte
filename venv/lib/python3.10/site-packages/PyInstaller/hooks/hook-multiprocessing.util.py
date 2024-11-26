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

# In Python 3.8 mutliprocess.utils has _cleanup_tests() to cleanup multiprocessing resources when multiprocessing tests
# completed. This function import `tests` which is the complete Python test-suite, pulling in many more dependencies,
# e.g., tkinter.

excludedimports = ['test']
