#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype slow cave** (i.e., private subset of the public :mod:`beartype.cave`
subpackage profiled to *not* be efficiently importable at :mod:`beartype`
startup and thus *not* safely importable throughout the internal
:mod:`beartype` codebase).

This submodule currently imports from expensive third-party packages on
importation (e.g., :mod:`numpy`) despite :mod:`beartype` itself *never*
requiring those imports. Until resolved, that subpackage is considered tainted.
'''

# ....................{ TODO                               }....................
#FIXME: Excise this submodule away, please. This submodule was a horrendous idea
#and has plagued the entire "beartype.cave" subpackage with unnecessary slowdown
#at import time. It's simply time for this to go, please.

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from argparse import (
    ArgumentParser,
    _SubParsersAction,
)
from weakref import (
    ProxyTypes,
    ref,
)

# ....................{ TYPES ~ lib                        }....................
# Types conditionally dependent upon the importability of third-party
# dependencies. These types are subsequently redefined by try-except blocks
# below and initially default to "UnavailableType" for simple types.

# ....................{ TYPES ~ stdlib : argparse          }....................
ArgParserType = ArgumentParser
'''
Type of argument parsers parsing all command-line arguments for either
top-level commands *or* subcommands of those commands.
'''


ArgSubparsersType = _SubParsersAction
'''
Type of argument subparser containers parsing subcommands for parent argument
parsers parsing either top-level commands *or* subcommands of those commands.
'''

# ....................{ TYPES ~ stdlib : weakref           }....................
WeakRefCType = ref
'''
Type of all **unproxied weak references** (i.e., callable objects yielding
strong references to their referred objects when called).

This type matches both the C-based :class:`weakref.ref` class *and* the
pure-Python :class:`weakref.WeakMethod` class, which subclasses the former.
'''
# ....................{ TUPLES ~ stdlib : weakref          }....................
WeakRefProxyCTypes = ProxyTypes
'''
Tuple of all **C-based weak reference proxy classes** (i.e., classes
implemented in low-level C whose instances are weak references to other
instances masquerading as those instances).

This tuple contains classes matching both callable and uncallable weak
reference proxies.
'''
