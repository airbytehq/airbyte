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
Automatically build a spec file containing the description of the project.
"""

import argparse
import os

import PyInstaller.building.makespec
import PyInstaller.log

try:
    from argcomplete import autocomplete
except ImportError:

    def autocomplete(parser):
        return None


def generate_parser():
    p = argparse.ArgumentParser()
    PyInstaller.building.makespec.__add_options(p)
    PyInstaller.log.__add_options(p)
    p.add_argument(
        'scriptname',
        nargs='+',
    )
    return p


def run():
    p = generate_parser()
    autocomplete(p)
    args = p.parse_args()
    PyInstaller.log.__process_options(p, args)

    # Split pathex by using the path separator.
    temppaths = args.pathex[:]
    args.pathex = []
    for p in temppaths:
        args.pathex.extend(p.split(os.pathsep))

    try:
        name = PyInstaller.building.makespec.main(args.scriptname, **vars(args))
        print('Wrote %s.' % name)
        print('Now run pyinstaller.py to build the executable.')
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


if __name__ == '__main__':
    run()
