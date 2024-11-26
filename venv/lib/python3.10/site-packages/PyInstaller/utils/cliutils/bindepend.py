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
"""
Show dll dependencies of executable files or other dynamic libraries.
"""

import argparse
import glob

import PyInstaller.depend.bindepend
import PyInstaller.log

try:
    from argcomplete import autocomplete
except ImportError:

    def autocomplete(parser):
        return None


def run():
    parser = argparse.ArgumentParser()
    PyInstaller.log.__add_options(parser)
    parser.add_argument(
        'filenames',
        nargs='+',
        metavar='executable-or-dynamic-library',
        help="executables or dynamic libraries for which the dependencies should be shown",
    )

    autocomplete(parser)
    args = parser.parse_args()
    PyInstaller.log.__process_options(parser, args)

    # Suppress all informative messages from the dependency code.
    PyInstaller.log.getLogger('PyInstaller.build.bindepend').setLevel(PyInstaller.log.WARN)

    try:
        for input_filename_or_pattern in args.filenames:
            for filename in glob.glob(input_filename_or_pattern):
                print(f"{filename}:")
                for lib_name, lib_path in sorted(PyInstaller.depend.bindepend.get_imports(filename)):
                    print(f"  {lib_name} => {lib_path}")
                print("")
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


if __name__ == '__main__':
    run()
