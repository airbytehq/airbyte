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
import os
import sys

# see https://github.com/giampaolo/psutil/blob/release-5.9.5/psutil/_common.py#L82
WINDOWS = os.name == "nt"
LINUX = sys.platform.startswith("linux")
MACOS = sys.platform.startswith("darwin")
FREEBSD = sys.platform.startswith(("freebsd", "midnightbsd"))
OPENBSD = sys.platform.startswith("openbsd")
NETBSD = sys.platform.startswith("netbsd")
BSD = FREEBSD or OPENBSD or NETBSD
SUNOS = sys.platform.startswith(("sunos", "solaris"))
AIX = sys.platform.startswith("aix")

excludedimports = [
    "psutil._pslinux",
    "psutil._pswindows",
    "psutil._psosx",
    "psutil._psbsd",
    "psutil._pssunos",
    "psutil._psaix",
]

# see https://github.com/giampaolo/psutil/blob/release-5.9.5/psutil/__init__.py#L97
if LINUX:
    excludedimports.remove("psutil._pslinux")
elif WINDOWS:
    excludedimports.remove("psutil._pswindows")
    # see https://github.com/giampaolo/psutil/blob/release-5.9.5/psutil/_common.py#L856
    # This will exclude `curses` for windows
    excludedimports.append("curses")
elif MACOS:
    excludedimports.remove("psutil._psosx")
elif BSD:
    excludedimports.remove("psutil._psbsd")
elif SUNOS:
    excludedimports.remove("psutil._pssunos")
elif AIX:
    excludedimports.remove("psutil._psaix")
