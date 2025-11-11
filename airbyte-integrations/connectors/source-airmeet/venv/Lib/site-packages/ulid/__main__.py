from __future__ import annotations

import argparse
import shutil
import sys
import textwrap
from datetime import datetime
from functools import partial
from typing import Any
from typing import TYPE_CHECKING
from uuid import UUID

import ulid
from ulid import ULID


if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Sequence


def make_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=textwrap.indent(
            textwrap.dedent(
                """
            Create or inspect ULIDs

            A ULID is a universally unique lexicographically sortable identifier
            with the following structure

               01AN4Z07BY      79KA1307SR9X4MV3
              |----------|    |----------------|
               Timestamp          Randomness
                 48bits             80bits
            """
            ).strip(),
            "    ",
        ),
        formatter_class=partial(
            argparse.RawDescriptionHelpFormatter,
            # Prevent argparse from taking up the entire width of the terminal window
            # which impedes readability.
            width=min(shutil.get_terminal_size().columns - 2, 127),
        ),
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument("--version", "-V", action="version", version=ulid.__version__)

    subparsers = parser.add_subparsers(title="subcommands")
    b = subparsers.add_parser(
        "build",
        help="generate ULIDs from different sources",
    )
    b.add_argument(
        "--from-int",
        metavar="<int>",
        help="create from integer",
    )
    b.add_argument(
        "--from-hex",
        metavar="<str>",
        help="create from 32 character hex value",
    )
    b.add_argument(
        "--from-str",
        metavar="<str>",
        help="create from base32 encoded string of length 26",
    )
    b.add_argument(
        "--from-timestamp",
        metavar="<int|float>",
        help="create from timestamp either as float in secs or int as millis",
    )
    b.add_argument(
        "--from-datetime",
        metavar="<iso8601>",
        help="create from datetime. The timestamp part of the ULID will be taken from the datetime",
    )
    b.add_argument(
        "--from-uuid",
        metavar="<uuid>",
        help="create from given UUID. The timestamp part will be random.",
    )
    b.set_defaults(func=build)

    s = subparsers.add_parser("show", help="show properties of a ULID")
    s.add_argument("ulid", help="the ULID to inspect. The special value - reads from stdin")
    s.add_argument("--uuid", action="store_true", help="convert to fully random UUID")
    s.add_argument("--uuid4", action="store_true", help="convert to RFC 4122 compliant UUIDv4")
    s.add_argument("--hex", action="store_true", help="convert to hex")
    s.add_argument("--int", action="store_true", help="convert to int")
    s.add_argument("--timestamp", "--ts", action="store_true", help="show timestamp")
    s.add_argument("--datetime", "--dt", action="store_true", help="show datetime")
    s.set_defaults(func=show)
    return parser


def main(argv: Sequence[str], prog: str | None = None) -> str:
    args = make_parser(prog).parse_args(argv)
    return args.func(args)


def from_value_or_stdin(value: str, convert: Callable[[str], Any] | None = None) -> Any:
    value = sys.stdin.readline().strip() if value == "-" else value
    if convert is not None:
        return convert(value)
    return value


def parse_numeric(s: str) -> int | float:
    try:
        return int(s)
    except ValueError:
        return float(s)


def build(args: argparse.Namespace) -> str:
    ulid: ULID
    if args.from_int is not None:
        ulid = ULID.from_int(from_value_or_stdin(args.from_int, int))
    elif args.from_hex is not None:
        ulid = ULID.from_hex(from_value_or_stdin(args.from_hex))
    elif args.from_str is not None:
        ulid = ULID.from_str(from_value_or_stdin(args.from_str))
    elif args.from_timestamp is not None:
        ulid = ULID.from_timestamp(from_value_or_stdin(args.from_timestamp, parse_numeric))
    elif args.from_datetime is not None:
        ulid = ULID.from_datetime(from_value_or_stdin(args.from_datetime, datetime.fromisoformat))
    elif args.from_uuid is not None:
        ulid = ULID.from_uuid(from_value_or_stdin(args.from_uuid, UUID))
    else:
        ulid = ULID()
    return str(ulid)


def show(args: argparse.Namespace) -> str:
    ulid: ULID = ULID.from_str(from_value_or_stdin(args.ulid))
    if args.uuid:
        return str(ulid.to_uuid())
    if args.uuid4:
        return str(ulid.to_uuid4())
    if args.hex:
        return ulid.hex
    if args.int:
        return str(int(ulid))
    if args.timestamp:
        return str(ulid.timestamp)
    if args.datetime:
        return ulid.datetime.isoformat()
    return textwrap.dedent(
        f"""
        ULID:      {ulid!s}
        Hex:       {ulid.hex}
        Int:       {int(ulid)}
        Timestamp: {ulid.timestamp}
        Datetime:  {ulid.datetime.isoformat()}
        """
    ).strip()


def entrypoint() -> None:  # pragma: no cover
    if (value := main(sys.argv[1:])) is not None:
        print(value)  # noqa: T201


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:], "python -m ulid")
