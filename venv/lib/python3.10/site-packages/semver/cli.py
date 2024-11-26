"""
CLI parsing for :command:`pysemver` command.

Each command in :command:`pysemver` is mapped to a ``cmd_`` function.
The :func:`main <semver.cli.main>` function calls
:func:`createparser <semver.cli.createparser>` and
:func:`process <semver.cli.process>` to parse and process
all the commandline options.

The result of each command is printed on stdout.
"""

import argparse
import sys
from typing import cast, List, Optional

from .version import Version
from .__about__ import __version__


def cmd_bump(args: argparse.Namespace) -> str:
    """
    Subcommand: Bumps a version.

    Synopsis: bump <PART> <VERSION>
    <PART> can be major, minor, patch, prerelease, or build

    :param args: The parsed arguments
    :return: the new, bumped version
    """
    maptable = {
        "major": "bump_major",
        "minor": "bump_minor",
        "patch": "bump_patch",
        "prerelease": "bump_prerelease",
        "build": "bump_build",
    }
    if args.bump is None:
        # When bump is called without arguments,
        # print the help and exit
        args.parser.parse_args(["bump", "-h"])

    ver = Version.parse(args.version)
    # get the respective method and call it
    func = getattr(ver, maptable[cast(str, args.bump)])
    return str(func())


def cmd_check(args: argparse.Namespace) -> None:
    """
    Subcommand: Checks if a string is a valid semver version.

    Synopsis: check <VERSION>

    :param args: The parsed arguments
    """
    if Version.is_valid(args.version):
        return None
    raise ValueError("Invalid version %r" % args.version)


def cmd_compare(args: argparse.Namespace) -> str:
    """
    Subcommand: Compare two versions.

    Synopsis: compare <VERSION1> <VERSION2>

    :param args: The parsed arguments
    """
    ver1 = Version.parse(args.version1)
    return str(ver1.compare(args.version2))


def cmd_nextver(args: argparse.Namespace) -> str:
    """
    Subcommand: Determines the next version, taking prereleases into account.

    Synopsis: nextver <VERSION> <PART>

    :param args: The parsed arguments
    """
    version = Version.parse(args.version)
    return str(version.next_version(args.part))


def createparser() -> argparse.ArgumentParser:
    """
    Create an :class:`argparse.ArgumentParser` instance.

    :return: parser instance
    """
    parser = argparse.ArgumentParser(prog=__package__, description=__doc__)

    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    s = parser.add_subparsers()
    # create compare subcommand
    parser_compare = s.add_parser("compare", help="Compare two versions")
    parser_compare.set_defaults(func=cmd_compare)
    parser_compare.add_argument("version1", help="First version")
    parser_compare.add_argument("version2", help="Second version")

    # create bump subcommand
    parser_bump = s.add_parser("bump", help="Bumps a version")
    parser_bump.set_defaults(func=cmd_bump)
    sb = parser_bump.add_subparsers(title="Bump commands", dest="bump")

    # Create subparsers for the bump subparser:
    for p in (
        sb.add_parser("major", help="Bump the major part of the version"),
        sb.add_parser("minor", help="Bump the minor part of the version"),
        sb.add_parser("patch", help="Bump the patch part of the version"),
        sb.add_parser("prerelease", help="Bump the prerelease part of the version"),
        sb.add_parser("build", help="Bump the build part of the version"),
    ):
        p.add_argument("version", help="Version to raise")

    # Create the check subcommand
    parser_check = s.add_parser(
        "check", help="Checks if a string is a valid semver version"
    )
    parser_check.set_defaults(func=cmd_check)
    parser_check.add_argument("version", help="Version to check")

    # Create the nextver subcommand
    parser_nextver = s.add_parser(
        "nextver", help="Determines the next version, taking prereleases into account."
    )
    parser_nextver.set_defaults(func=cmd_nextver)
    parser_nextver.add_argument("version", help="Version to raise")
    parser_nextver.add_argument(
        "part", help="One of 'major', 'minor', 'patch', or 'prerelease'"
    )
    return parser


def process(args: argparse.Namespace) -> str:
    """
    Process the input from the CLI.

    :param args: The parsed arguments
    :param parser: the parser instance
    :return: result of the selected action
    """
    if not hasattr(args, "func"):
        args.parser.print_help()
        raise SystemExit()

    # Call the respective function object:
    return args.func(args)


def main(cliargs: Optional[List[str]] = None) -> int:
    """
    Entry point for the application script.

    :param list cliargs: Arguments to parse or None (=use :class:`sys.argv`)
    :return: error code
    """
    try:
        parser = createparser()
        args = parser.parse_args(args=cliargs)
        # Save parser instance:
        args.parser = parser
        result = process(args)
        if result is not None:
            print(result)
        return 0

    except (ValueError, TypeError) as err:
        print("ERROR", err, file=sys.stderr)
        return 2
