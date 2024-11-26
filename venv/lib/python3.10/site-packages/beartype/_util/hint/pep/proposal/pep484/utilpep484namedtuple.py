#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **named tuple utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant named tuples -- which
is to say, instances of concrete subclasses of the standard
:attr:`typing.NamedTuple` superclass).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.cls.utilclstest import is_type_subclass_proper
# from beartype.roar import BeartypeDecorHintPep484Exception
# from beartype.typing import Any
# from beartype._data.hint.pep.sign.datapepsigns import HintSignNewType
# from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
# from types import FunctionType

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
#FIXME: Actually call this tester in the get_hint_pep_sign_or_none() getter to
#map "typing.NamedTuple" subclasses to the "HintSignNamedTuple" sign, please.
#FIXME: Actually type-check type hints identified by the "HintSignNamedTuple"
#sign. Specifically, for each "typing.NamedTuple" subclass identified by that
#sign, type-check that subclass as follows:
#* If that subclass is decorated by @beartype, reduce to the standard trivial
#  isinstance() check. Since @beartype already type-checks instances of that
#  subclass on instantiation, *NO* further type-checking is required or desired.
#* Else, that subclass is *NOT* decorated by @beartype. In this case, matters
#  become considerably non-trivial. Why? Because:
#  * This situation commonly arises when type-checking "typing.NamedTuple"
#    subclasses *NOT* under user control (e.g., defined by upstream third-party
#    packages in an app stack). Since these subclasses are *NOT* under user
#    control, there exists *NO* safe means for @beartype to monkey-patch these
#    subclasses with itself. Ergo, instances of these subclasses are guaranteed
#    to *NOT* be type-checked at instantiation time.
#  * The prior point implies that @beartype must instead type-check instances of
#    these subclasses at @beartype call time. However, the naive approach to
#    doing so is likely to prove inefficient. The naive approach is simply to
#    type-check *ALL* fields of these instances *EVERY* time these instances are
#    type-checked at @beartype call time. Since these fields could themselves
#    refer to other "typing.NamedTuple" subclasses, combinatorial explosion
#    violating O(1) constraints becomes a real possibility here.
#  * *RECURSION.* Both direct and indirect recursion are feasible here. Both
#    require PEP 563 and are thus unlikely. Nonetheless:
#    * Direct recursion occurs under PEP 563 as follows:
#          from __future__ import annotations
#          from typing import NamedTuple
#
#          class DirectlyRecursiveNamedTuple(NamedTuple):
#              uhoh: DirectlyRecursiveNamedTuple
#    * Indirect recursion occurs  as PEP 563 follows:
#          from typing import NamedTuple
#
#          class IndirectlyRecursiveNamedTuple(NamedTuple):
#              uhoh: YetAnotherNamedTuple
#
#          class YetAnotherNamedTuple(NamedTuple):
#              ohboy: IndirectlyRecursiveNamedTuple
#
#Guarding against both combinatorial explosion *AND* recursion is imperative. To
#do so, we'll need to fundamentally refactor our existing breadth-first search
#(BFS) over type hints into a new depth-first search (DFS) over type hints.
#We've extensively documented this in the "beartype._check.code.__init__"
#submodule. Simply know that this will be non-trivial, albeit fun and needed!
def is_hint_pep484_namedtuple_subclass(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a :pep:`484`-compliant **named tuple
    subclass** (i.e., concrete subclass of the standard
    :attr:`typing.NamedTuple` superclass).

    Note that the :attr:`typing.NamedTuple` attribute is *not* actually a
    superclass; that attribute only superficially masquerades (through
    inscrutable metaclass trickery) as a superclass. As one might imagine,
    detecting "subclasses" of a non-existent superclass is non-trivial.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`484`-compliant named tuple
        subclass.
    '''

    # Return true only if...
    return (
        # This hint is a proper tuple subclass (i.e., subclass of the builtin
        # "tuple" type but *NOT* that type itself) *AND*...
        is_type_subclass_proper(hint, tuple) and
        #FIXME: Implement us up, please. To do so efficiently, we'll probably
        #want to:
        #* Declare a private global frozenset of the names of all uniquely
        #  identifying "typing.NamedTuple" attributes: e.g.,
        #  _NAMEDTUPLE_UNIQUE_ATTR_NAMES = frozenset((
        #      # "typing.NamedTuple"-specific quasi-public attributes.
        #      '__annotations__',
        #
        #      # "collections.namedtuple"-specific quasi-public attributes.
        #      '_asdict',
        #      '_field_defaults',
        #      '_fields',
        #      '_make',
        #      '_replace',
        #  ))
        #* Efficiently take the set intersection of that frozenset and
        #  "dir(tuple)". If that intersection is non-empty, then this type is
        #  *PROBABLY* a "typing.NamedTuple" subclass.
        #
        #Note that there does exist an alternative. Sadly, that alternative
        #requires an O(n) test and is thus non-ideal. Nonetheless:
        #    typing.NamedTuple in getattr(hint, '__orig_bases__', ())
        #
        #That *DOES* have the advantage of being deterministic. But the above
        #set intersection test is mostly deterministic and considerably
        #faster... we think. Actually, is it? We have *NO* idea. Perhaps we
        #should simply opt for the simplistic and deterministic O(n) approach.
        True
    )
