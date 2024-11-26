#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Python Enhancement Proposal (PEP) API.**

This subpackage provides a medley of miscellaneous low-level utility functions
implementing unofficial (albeit well-tested) runtime support for PEPs lacking
official runtime support in CPython's standard library. This subpackage is
intended to be used both by downstream third-party packages and the
:mod:`beartype` codebase itself. Supported PEPs include:

* :pep:`563` (i.e., "Postponed Evaluation of Annotations") via the
  :func:`resolve_pep563` function.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.peps._pep563 import (
    resolve_pep563 as resolve_pep563)
