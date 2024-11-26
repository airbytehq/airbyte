"""
Module to support call with :file:`__main__.py`. Used to support the following
call::

    $ python3 -m semver ...

This makes it also possible to "run" a wheel like in this command::

    $ python3 semver-3*-py3-none-any.whl/semver -h

"""
import os.path
import sys
from typing import List, Optional

from semver import cli


def main(cliargs: Optional[List[str]] = None) -> int:
    if __package__ == "":
        path = os.path.dirname(os.path.dirname(__file__))
        sys.path[0:0] = [path]

    return cli.main(cliargs)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
