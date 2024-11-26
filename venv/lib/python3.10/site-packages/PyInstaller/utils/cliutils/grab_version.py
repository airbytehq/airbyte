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
import codecs

try:
    from argcomplete import autocomplete
except ImportError:

    def autocomplete(parser):
        return None


def run():
    parser = argparse.ArgumentParser(
        epilog=(
            'The printed output may be saved to a file, edited and used as the input for a version resource on any of '
            'the executable targets in a PyInstaller .spec file.'
        )
    )
    parser.add_argument(
        'exe_file',
        metavar='exe-file',
        help="full pathname of a Windows executable",
    )
    parser.add_argument(
        'out_filename',
        metavar='out-filename',
        nargs='?',
        default='file_version_info.txt',
        help="filename where the grabbed version info will be saved",
    )

    autocomplete(parser)
    args = parser.parse_args()

    try:
        from PyInstaller.utils.win32 import versioninfo
        info = versioninfo.read_version_info_from_executable(args.exe_file)
        if not info:
            raise SystemExit("Error: VersionInfo resource not found in exe")
        with codecs.open(args.out_filename, 'w', 'utf-8') as fp:
            fp.write(str(info))
        print(f"Version info written to: {args.out_filename!r}")
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


if __name__ == '__main__':
    run()
