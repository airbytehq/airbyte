# ------------------------------------------------------------------
# Copyright (c) 2023 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_data_files

# `z3c.rml` uses Bitstream Vera TTF fonts from the `reportlab` package. As that package can be used without the bundled
# fonts and as some of the bundled fonts have restrictive license (e.g., DarkGarden), we collect the required subset
# of fonts here, instead of collecting them all in a hook for `reportlab`.
datas = collect_data_files(
    "reportlab",
    includes=[
        "fonts/00readme.txt",
        "fonts/bitstream-vera-license.txt",
        "fonts/Vera*.ttf",
    ],
)
