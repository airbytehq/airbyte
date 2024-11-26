"""
Internal helpers for basic commandline tools
"""
from __future__ import absolute_import, print_function

import os
import sys

from macholib.util import is_platform_file


def check_file(fp, path, callback):
    if not os.path.exists(path):
        print(
            "%s: %s: No such file or directory" % (sys.argv[0], path), file=sys.stderr
        )
        return 1

    try:
        is_plat = is_platform_file(path)

    except IOError as msg:
        print("%s: %s: %s" % (sys.argv[0], path, msg), file=sys.stderr)
        return 1

    else:
        if is_plat:
            callback(fp, path)
    return 0


def main(callback):
    args = sys.argv[1:]
    name = os.path.basename(sys.argv[0])
    err = 0

    if not args:
        print("Usage: %s filename..." % (name,), file=sys.stderr)
        return 1

    for base in args:
        if os.path.isdir(base):
            for root, _dirs, files in os.walk(base):
                for fn in files:
                    err |= check_file(sys.stdout, os.path.join(root, fn), callback)
        else:
            err |= check_file(sys.stdout, base, callback)

    return err
