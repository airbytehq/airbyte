#!/usr/bin/env python

import os
import sys

from macholib.MachOStandalone import MachOStandalone
from macholib.util import strip_files


def standaloneApp(path):
    if not (os.path.isdir(path) and os.path.exists(os.path.join(path, "Contents"))):
        print("%s: %s does not look like an app bundle" % (sys.argv[0], path))
        sys.exit(1)
    files = MachOStandalone(path).run()
    strip_files(files)


def main():
    print(
        "WARNING: 'macho_standalone' is deprecated, use "
        "'python -mmacholib standalone' instead"
    )
    if not sys.argv[1:]:
        raise SystemExit("usage: %s [appbundle ...]" % (sys.argv[0],))
    for fn in sys.argv[1:]:
        standaloneApp(fn)


if __name__ == "__main__":
    main()
