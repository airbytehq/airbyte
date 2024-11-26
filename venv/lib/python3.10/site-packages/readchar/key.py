# flake8: noqa E401,E403
# this file exists only for backwards compatability
# it allow the use of `import readchar.key`

from . import platform


if platform.startswith(("linux", "darwin", "freebsd")):
    from ._posix_key import *
elif platform in ("win32", "cygwin"):
    from ._win_key import *
else:
    raise NotImplementedError(f"The platform {platform} is not supported yet")
