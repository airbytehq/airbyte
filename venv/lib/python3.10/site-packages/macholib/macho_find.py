#!/usr/bin/env python
from __future__ import print_function

from macholib._cmdline import main as _main


def print_file(fp, path):
    print(path, file=fp)


def main():
    print(
        "WARNING: 'macho_find' is deprecated, " "use 'python -mmacholib dump' instead"
    )
    _main(print_file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
