#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hints** (i.e., PEP-compliant type hints annotating callables
and classes declared throughout this codebase, either for compliance with
:pep:`561`-compliant static type checkers like :mod:`mypy` or simply for
documentation purposes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: This approach is *PHENOMENAL.* No. Seriously, We could implement a
#full-blown "beartype.typing" subpackage (or perhaps even separate "beartyping"
#package) extending this core concept to *ALL* type hint factories, enabling
#users to trivially annotate with any type hint factory regardless of the
#current version of Python or whether "typing_extensions" is installed or not.

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
)
from beartype._util.hint.utilhintfactory import TypeHintTypeFactory
from beartype._util.module.lib.utiltyping import import_typing_attr_or_fallback

# ....................{ FACTORIES                          }....................
# Portably import the PEP 647-compliant "typing.TypeGuard" type hint factory
# first introduced by Python >= 3.10, regardless of the current version of
# Python and regardless of whether this submodule is currently being subject to
# static type-checking or not. Praise be to MIT ML guru and stunning Hypothesis
# maintainer @rsokl (Ryan Soklaski) for this brilliant circumvention. \o/
#
# Usage of this factory is a high priority. Hinting the return of the
# is_bearable() tester with a type guard created by this factory effectively
# coerces that tester in an arbitrarily complete type narrower and thus type
# parser at static analysis time, substantially reducing complaints from static
# type-checkers in end user code deferring to that tester.
#
# If this submodule is currently being statically type-checked (e.g., mypy),
# intentionally import from the third-party "typing_extensions" module rather
# than the standard "typing" module. Why? Because doing so eliminates Python
# version complaints from static type-checkers (e.g., mypy, pyright). Static
# type-checkers could care less whether "typing_extensions" is actually
# installed or not; they only care that "typing_extensions" unconditionally
# defines this type factory across all Python versions, whereas "typing" only
# conditionally defines this type factory under Python >= 3.10. *facepalm*
if TYPE_CHECKING:
    from typing_extensions import TypeGuard as TypeGuard
# Else, this submodule is currently being imported at runtime by Python. In this
# case, dynamically import this factory from whichever of the standard "typing"
# module *OR* the third-party "typing_extensions" module declares this factory,
# falling back to the builtin "bool" type if none do.
else:
    TypeGuard = import_typing_attr_or_fallback(
        'TypeGuard', TypeHintTypeFactory(bool))
