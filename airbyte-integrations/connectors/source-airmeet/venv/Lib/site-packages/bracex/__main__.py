"""
Expands a bash-style brace expression, and outputs each expansion.

Licensed under MIT
Copyright (c) 2018 - 2020 Isaac Muse <isaacmuse@gmail.com>
Copyright (c) 2021 Alex Willmer <alex@moreati.org.uk>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import annotations
import argparse
import bracex


def main(argv: str | None = None) -> None:
    """Accept command line arguments and output brace expansion to stdout."""
    parser = argparse.ArgumentParser(
        prog='python -m bracex',
        description='Expands a bash-style brace expression, and outputs each expansion.',
        allow_abbrev=False,
    )
    parser.add_argument(
        'expression',
        help="Brace expression to expand",
    )
    terminators = parser.add_mutually_exclusive_group()
    terminators.add_argument(
        '--terminator', '-t',
        default='\n',
        metavar='STR',
        help="Terminate each expansion with string STR (default: \\n)",
    )
    terminators.add_argument(
        '-0',
        action='store_const',
        const='\0',
        dest='terminator',
        help="Terminate each expansion with a NUL character",
    )
    parser.add_argument(
        '--version',
        action='version',
        version=bracex.__version__,
    )

    args = parser.parse_args(argv)

    for expansion in bracex.iexpand(args.expression, limit=0):
        print(expansion, end=args.terminator)

    raise SystemExit(0)


if __name__ == '__main__':
    main()  # pragma: no cover
