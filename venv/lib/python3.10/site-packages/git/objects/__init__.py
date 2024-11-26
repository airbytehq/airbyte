# This module is part of GitPython and is released under the
# 3-Clause BSD License: https://opensource.org/license/bsd-3-clause/

"""Import all submodules' main classes into the package space."""

import inspect

from .base import *  # noqa: F403
from .blob import *  # noqa: F403
from .commit import *  # noqa: F403
from .submodule import util as smutil
from .submodule.base import *  # noqa: F403
from .submodule.root import *  # noqa: F403
from .tag import *  # noqa: F403
from .tree import *  # noqa: F403

# Fix import dependency - add IndexObject to the util module, so that it can be
# imported by the submodule.base.
smutil.IndexObject = IndexObject  # type: ignore[attr-defined]  # noqa: F405
smutil.Object = Object  # type: ignore[attr-defined]  # noqa: F405
del smutil

# Must come after submodule was made available.
__all__ = [name for name, obj in locals().items() if not (name.startswith("_") or inspect.ismodule(obj))]
