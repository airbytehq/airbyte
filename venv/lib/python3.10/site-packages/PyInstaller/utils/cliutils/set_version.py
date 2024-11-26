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

import argparse
import os

try:
    from argcomplete import autocomplete
except ImportError:

    def autocomplete(parser):
        return None


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'info_file',
        metavar='info-file',
        help="text file containing version info",
    )
    parser.add_argument(
        'exe_file',
        metavar='exe-file',
        help="full pathname of a Windows executable",
    )
    autocomplete(parser)
    args = parser.parse_args()

    info_file = os.path.abspath(args.info_file)
    exe_file = os.path.abspath(args.exe_file)

    try:
        from PyInstaller.utils.win32 import versioninfo
        info = versioninfo.load_version_info_from_text_file(info_file)
        versioninfo.write_version_info_to_executable(exe_file, info)
        print(f"Version info written to: {exe_file!r}")
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


if __name__ == '__main__':
    run()
