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
Viewer for PyInstaller-generated archives.
"""

import argparse
import os
import sys

import PyInstaller.log
from PyInstaller.archive.readers import CArchiveReader, ZlibArchiveReader

try:
    from argcomplete import autocomplete
except ImportError:

    def autocomplete(parser):
        return None


class ArchiveViewer:
    def __init__(self, filename, interactive_mode, recursive_mode, brief_mode):
        self.filename = filename
        self.interactive_mode = interactive_mode
        self.recursive_mode = recursive_mode
        self.brief_mode = brief_mode

        self.stack = []

        # Recursive mode implies non-interactive mode
        if self.recursive_mode:
            self.interactive_mode = False

    def main(self):
        # Open top-level (initial) archive
        archive = self._open_toplevel_archive(self.filename)
        archive_name = os.path.basename(self.filename)
        self.stack.append((archive_name, archive))

        # Not-interactive mode
        if not self.interactive_mode:
            return self._non_interactive_processing()

        # Interactive mode; show top-level archive
        self._show_archive_contents(archive_name, archive)

        # Interactive command processing
        while True:
            # Read command
            try:
                tokens = input('? ').split(None, 1)
            except EOFError:
                # Ctrl-D
                print(file=sys.stderr)  # Clear line.
                break

            # Print usage?
            if not tokens:
                self._print_usage()
                continue

            # Process
            command = tokens[0].upper()
            if command == 'Q':
                break
            elif command == 'U':
                self._move_up_the_stack()
            elif command == 'O':
                self._open_embedded_archive(*tokens[1:])
            elif command == 'X':
                self._extract_file(*tokens[1:])
            elif command == 'S':
                archive_name, archive = self.stack[-1]
                self._show_archive_contents(archive_name, archive)
            else:
                self._print_usage()

    def _non_interactive_processing(self):
        archive_count = 0

        while self.stack:
            archive_name, archive = self.stack.pop()
            archive_count += 1

            if archive_count > 1:
                print("")
            self._show_archive_contents(archive_name, archive)

            if not self.recursive_mode:
                continue

            # Scan for embedded archives
            if isinstance(archive, CArchiveReader):
                for name, (*_, typecode) in archive.toc.items():
                    if typecode == 'z':
                        try:
                            embedded_archive = archive.open_embedded_archive(name)
                        except Exception as e:
                            print(f"Could not open embedded archive {name!r}: {e}", file=sys.stderr)
                        self.stack.append((name, embedded_archive))

    def _print_usage(self):
        print("U: go up one level", file=sys.stderr)
        print("O <name>: open embedded archive with given name", file=sys.stderr)
        print("X <name>: extract file with given name", file=sys.stderr)
        print("S: list the contents of current archive again", file=sys.stderr)
        print("Q: quit", file=sys.stderr)

    def _move_up_the_stack(self):
        if len(self.stack) > 1:
            self.stack.pop()
            archive_name, archive = self.stack[-1]
            self._show_archive_contents(archive_name, archive)
        else:
            print("Already in the top archive!", file=sys.stderr)

    def _open_toplevel_archive(self, filename):
        if not os.path.isfile(filename):
            print(f"Archive {filename} does not exist!", file=sys.stderr)
            sys.exit(1)

        if filename[-4:].lower() == '.pyz':
            return ZlibArchiveReader(filename)
        return CArchiveReader(filename)

    def _open_embedded_archive(self, archive_name=None):
        # Ask for name if not provided
        if not archive_name:
            archive_name = input('Open name? ')
        archive_name = archive_name.strip()

        # No name given; abort
        if not archive_name:
            return

        # Open the embedded archive
        _, parent_archive = self.stack[-1]

        if not hasattr(parent_archive, 'open_embedded_archive'):
            print("Archive does not support embedded archives!", file=sys.stderr)
            return

        try:
            archive = parent_archive.open_embedded_archive(archive_name)
        except Exception as e:
            print(f"Could not open embedded archive {archive_name!r}: {e}", file=sys.stderr)
            return

        # Add to stack and display contents
        self.stack.append((archive_name, archive))
        self._show_archive_contents(archive_name, archive)

    def _extract_file(self, name=None):
        # Ask for name if not provided
        if not name:
            name = input('Extract name? ')
        name = name.strip()

        # Archive
        archive_name, archive = self.stack[-1]

        # Retrieve data
        try:
            if isinstance(archive, CArchiveReader):
                data = archive.extract(name)
            elif isinstance(archive, ZlibArchiveReader):
                data = archive.extract(name, raw=True)
            else:
                raise NotImplementedError(f"Extraction from archive type {type(archive)} not implemented!")
        except Exception as e:
            print(f"Failed to extract data for entry {name!r} from {archive_name!r}: {e}", file=sys.stderr)

        # Write to file
        filename = input('Output filename? ')
        if not filename:
            print(repr(data))
        else:
            with open(filename, 'wb') as fp:
                fp.write(data)

    def _show_archive_contents(self, archive_name, archive):
        if isinstance(archive, CArchiveReader):
            if archive.options:
                print(f"Options in {archive_name!r} (PKG/CArchive):")
                for option in archive.options:
                    print(f" {option}")
            print(f"Contents of {archive_name!r} (PKG/CArchive):")
            if self.brief_mode:
                for name in archive.toc.keys():
                    print(f" {name}")
            else:
                print(" position, length, uncompressed_length, is_compressed, typecode, name")
                for name, (position, length, uncompressed_length, is_compressed, typecode) in archive.toc.items():
                    print(f" {position}, {length}, {uncompressed_length}, {is_compressed}, {typecode!r}, {name!r}")
        elif isinstance(archive, ZlibArchiveReader):
            print(f"Contents of {archive_name!r} (PYZ):")
            if self.brief_mode:
                for name in archive.toc.keys():
                    print(f" {name}")
            else:
                print(" is_package, position, length, name")
                for name, (is_package, position, length) in archive.toc.items():
                    print(f" {is_package}, {position}, {length}, {name!r}")
        else:
            print(f"Contents of {name} (unknown)")
            print(f"FIXME: implement content listing for archive type {type(archive)}!")


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l',
        '--list',
        default=False,
        action='store_true',
        dest='listing_mode',
        help='List the archive contents and exit (default: %(default)s).',
    )
    parser.add_argument(
        '-r',
        '--recursive',
        default=False,
        action='store_true',
        dest='recursive',
        help='Recursively print an archive log (default: %(default)s). Implies --list.',
    )
    parser.add_argument(
        '-b',
        '--brief',
        default=False,
        action='store_true',
        dest='brief',
        help='When displaying archive contents, show only file names. (default: %(default)s).',
    )
    PyInstaller.log.__add_options(parser)
    parser.add_argument(
        'filename',
        metavar='pyi_archive',
        help="PyInstaller archive to process.",
    )

    autocomplete(parser)
    args = parser.parse_args()
    PyInstaller.log.__process_options(parser, args)

    try:
        viewer = ArchiveViewer(
            filename=args.filename,
            interactive_mode=not args.listing_mode,
            recursive_mode=args.recursive,
            brief_mode=args.brief,
        )
        viewer.main()
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user.")


if __name__ == '__main__':
    run()
