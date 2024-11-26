#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype plugin mixin hierarchy** (i.e., public classes intended to be
subclassed as mixins by users extending :mod:`beartype` with third-party runtime
behaviours).

Most of the public attributes defined by this private submodule are explicitly
exported to external users in our top-level :mod:`beartype.plug.__init__`
submodule. This private submodule is *not* intended for direct importation by
downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Optional,
    Tuple,
)
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ MIXINS                             }....................
class BeartypeHintable(object):
    '''
    **Beartype hintable mixin** (i.e., class intended to be subclassed as a
    mixin by user-defined classes extending :mod:`beartype` with class-specific
    runtime type-checking via the :mod:`beartype`-specific
    :meth:`__beartype_hint__` method).

    Usage
    ----------
    **You are encouraged but not required to subclass this mixin.** Doing so
    publicly declares your intention to implement this abstract method and then
    raises a :exc:`NotImplementedError` exception when you fail to do so,
    improving the quality of your codebase with a simple contractual guarantee.
    This mixin does *not* require a custom metaclass and is thus safely
    subclassable by everything -- including your own classes.

    **Beartype internally ignores this mixin.** This mixin exists *only* to
    improve the quality of your codebase. Instead, beartype detects type hints
    defining :meth:`__beartype_hint__` methods via the :func:`getattr` builtin
    and then replaces those hints with the new type hints returned by those
    methods. In pseudo-code, this logic crudely resembles: e.g.,

    .. code-block:: python

       # "__beartype_hint__" attribute of this type hint if any *OR* "None".
       beartype_hinter = getattr(hint, '__beartype_hint__')

       # If this hint defines this method, replace this hint with the new type
       # hint created and returned by this method.
       if callable(beartype_hinter):
           hint = beartype_hinter()

    You care about this, because this means that:

    * You can trivially monkey-patch third-party classes *not* under your direct
      control with :meth:`__beartype_hint__` methods, constraining those classes
      with runtime type-checking implemented by you!
    * :mod:`beartype` accepts *any* arbitrary objects defining
      :meth:`__beartype_hint__` methods as valid type hints -- including objects
      that are neither classes nor PEP-compliant! Of course, doing so would
      render your code incompatible with static type-checkers and thus IDEs.
      That's a bad thing. Nonetheless, this API enables you to do bad things.
      With great plugin power comes great user responsibility.
    '''

    # ....................{ METHODS                        }....................
    @classmethod
    def __beartype_hint__(cls) -> object:
        '''
        **Beartype type hint transform** (i.e., :mod:`beartype`-specific dunder
        class method returning a new type hint, which typically constrains this
        class with additional runtime type-checking).
        '''

        raise NotImplementedError(  # pragma: no cover
            'Abstract base class method '
            'BeartypeHintable.__beartype_hint__() undefined.'
        )

# ....................{ TESTERS                            }....................
#FIXME: Document us up, please.
#FIXME: Unit test us up, please.
#FIXME: Call us elsewhere, please.
@callable_cached
def is_hint_beartypehintable(hint: object) -> bool:

    # Return true only if this hint defines the "__beartype_hint__" attribute.
    return hasattr(hint, '__beartype_hint__')

# ....................{ TRANSFORMERS ~ more than meets the }....................
# ....................{                                eye }....................
#FIXME: Document us up, please.
#FIXME: Unit test us up, please.
#FIXME: Significant complications exist suggesting that we should immediately
#release beartype 0.12.0 and contemplate implementing this later:
#* The "beartype._decor.error" subpackage will need to implement a comparable
#  mechanism as the "beartype._check.code" subpackage for detecting and avoiding
#  recursion in this reduction. Curiously, "beartype._decor.error" only ever
#  calls the sanify_hint_any() sanifier in a single place. That simplifies
#  things a bit. Still, we'll need to add a similar "set" somewhere in that
#  subpackage tracking which "BeartypeHintable" objects have already been
#  reduced.
#* Even ignoring that, detecting and avoiding recursion in
#  "beartype._check.code" alone will be non-trivial. We can't pass the original
#  presanified type hint to the make_check_expr() factory, because that hint has
#  *NOT* been coerced into a memoizable singleton (e.g., think PEP 585). That
#  means the caller needs to pass either:
#  * A boolean "is_hint_beartypehintable" parameter that is true only if the
#    presanified root type hint was a "BeartypeHintable".
#  * A "beartypehintables: Optional[set]" parameter that is a non-empty set
#    containing the presanified root type hint if that hint was a
#    "BeartypeHintable" *OR* "None" otherwise.
#  The caller can trivially detect "BeartypeHintable" hints by calling the
#  is_hint_beartypehintable() tester defined above. That's *NOT* the issue,
#  thankfully. The issue is that we call sanify_*_root() functions in exactly
#  three different places. We'll now need to duplicate this detection of
#  "BeartypeHintable" hints across those three different places. Is this
#  something we *REALLY* want to do? Is there truly no better way?
#
#Examining the code calling sanify_*_root() functions, it superficially looks
#like we might want to consider *NO LONGER DEFINING OR CALLING* sanify_*_root()
#functions. Like, seriously. The logic performed by those functions has become
#trivial. They're practically one-liners. That said, sanify_hint_any() is
#still extremely useful and should be preserved exactly as is. Consider:
#* High-level functions calling sanify_*_root() functions should instead just
#  call either coerce_func_hint_root() or coerce_hint_root() based on context.
#  Those functions should *NOT* call reduce_hint() anymore.
#* Excise up all sanify_*_root() functions.
#* The make_check_expr() function should now call:
#  * On the passed root type hint:
#       if is_hint_beartypehintable(hint_root):
#           hint_parent_beartypehintables = {hint_root,}
#           hint_root = transform_hint_beartypehintable(hint_root)
#
#       hint_root = reduce_hint(hint_root)
#  * On each child type hint:
#       # This exact logic is likely to be duplicated into
#       # "beartype._decor.error". That's not particularly a problem -- just
#       # something worth noting. One approach to preserving DRY here would be
#       # to shift this "if" statement into sanify_hint_any(). Of course,
#       # everything then becomes non-trivial, because we would then need to
#       # both pass *AND* return "hint_parent_beartypehintables" sets to and
#       # from the sanify_hint_any() function. *sigh*
#       if (
#           is_hint_beartypehintable(hint_child) and
#           hint_child not in hint_parent_beartypehintables
#       ):
#           if hint_parent_beartypehintables is None:
#               hint_parent_beartypehintables  = {hint_child,}
#           else:
#               hint_parent_beartypehintables |= {hint_child,}
#
#           hint_child = transform_hint_beartypehintable(hint_child)
#
#       hint_child = sanify_hint_any(hint_root)
#FIXME: Wow. What a fascinatingly non-trivial issue. The above doesn't work,
#either. Why? Two reasons:
#* sanify_*_root() functions *MUST* continue to perform reduction -- including
#  calling both reduce_hint() and transform_hint_beartypehintable(). Why? Because
#  reduction *MUST* be performed before deciding "is_hint_ignorable", which
#  *MUST* be decided before generating code. This is non-optional.
#* transform_hint_beartypehintable() *CANNOT* be performed in either:
#  * reduce_hint(), because reduce_hint() is memoized but
#    transform_hint_beartypehintable() is non-memoizable by definition.
#  * coerce_*_hint(), because coerce_*_hint() is permanently applied to
#    "__annotations__" but transform_hint_beartypehintable() should *NEVER* be.
#
#Altogether, this suggests that:
#* All sanify_*() functions *MUST* call transform_hint_beartypehintable()
#  directly, outside of calls to either reduce_hint() and coerce_*_hint().
#* Frozensets should be used. Doing so enables memoization, if we wanted.
#* Call transform_hint_beartypehintable() from sanify_hint_any(), whose
#  signature *MUST* be augmented accordingly (i.e., to both accept and return
#  "hints_parent_beartypehintable: Optional[frozenset]").
#* Call transform_hint_beartypehintable() from sanify_*hint_root(), whose
#  signatures *MUST* be augmented accordingly (i.e., to additionally return
#  "Optional[frozenset]").
#* Augment make_check_expr() to:
#  * Accept an additional
#    "hints_parent_beartypehintable: Optional[frozenset]," parameter.
#  * Add yet another new entry to each "hint_meta" FixedList as follows:
#    * Define a new "HINT_META_INDEX_HINTS_PARENT_BEARTYPEHINTABLE" constant.
#    * For the root "hint_meta", initialize the value of:
#          hint_root_meta[HINT_META_INDEX_HINTS_PARENT_BEARTYPEHINTABLE] = (
#              hints_parent_beartypehintable)
#* Restore unit testing in "_data_nonpepbeartype", please.
#
#That should more or less do it, folks. Phew! It's still sufficiently
#non-trivial that we want to defer this until *AFTER* beartype 0.12.0, though.

#FIXME: Unit test us up, please.
#FIXME: Document us up, please.
@callable_cached
def transform_hint_beartypehintable(
    hint: object,
    hints_parent_beartypehintable: Optional[frozenset],
) -> Tuple[object, Optional[frozenset]]:

    # ..................{ PLUGIN                             }..................
    # Beartype plugin API. Respect external user-defined classes satisfying the
    # beartype plugin API *BEFORE* handling these classes in any way.

    # If this hint has already been transformed by a prior call to this
    # function, preserve this hint as is. Doing so avoids infinite recursion and
    # is, indeed, the entire point of the "hints_parent_beartypehintable" set.
    if (
        hints_parent_beartypehintable and
        hint in hints_parent_beartypehintable
    ):
        return (hint, hints_parent_beartypehintable)
    # Else, this hint has *NOT* yet been transformed by such a call.

    # Beartype-specific "__beartype_hint__" attribute defined by this hint if
    # any *OR* "None" otherwise.
    #
    # Note that usage of the low-level getattr() builtin is intentional. *ALL*
    # alternative higher-level approaches suffer various deficits, including:
    # * Obstructing monkey-patching. The current approach trivializes
    #   monkey-patching by third parties, enabling users to readily add
    #   __beartype_hint__() support to third-party packages *NOT* under their
    #   direct control. Alternative higher-level approaches obstruct that by
    #   complicating (or just outright prohibiting) monkey-patching.
    # * Abstract base classes (ABCs) assume that hints that are classes are
    #   issubclassable (i.e., safely passable as the first arguments of the
    #   issubclass() builtin). Sadly, various real-world hints that are classes
    #   are *NOT* issubclassable. This includes the core
    #   "typing.NDArray[{dtype}]" type hints, astonishingly. Of course, even
    #   this edge case could be surmounted by explicitly testing for
    #   issubclassability (e.g., by calling our existing
    #   is_type_issubclassable() tester); since that tester internally leverages
    #   the inefficient Easier to Ask for Forgiveness than Permission (EAFP)
    #   paradigm, doing so would impose a measurable performance penalty. This
    #   only compounds the monkey-patching complications that an ABC imposes.
    # * PEP 544-compliant protocols assume that the active Python interpreter
    #   supports PEP 544, which Python 3.7 does not. While Python 3.7 has
    #   probably hit its End of Life (EOL) by the time you are reading this,
    #   additional issue exist. On the one hand, protocols impose even *MORE* of
    #   a performance burden than ABCs. On the other hand, protocols ease the
    #   user-oriented burden of monkey-patching.
    #
    # In short, this low-level approach effectively imposes *NO* burdens at all.
    # There exists *NO* reason to prefer higher-level alternatives.
    __beartype_hint__ = getattr(hint, '__beartype_hint__', None)

    # If this hint does *NOT* define the "__beartype_hint__" attribute, preserve
    # this hint as is.
    if __beartype_hint__ is None:
        return (hint, hints_parent_beartypehintable)
    # Else, this hint defines the "__beartype_hint__" attribute.

    #FIXME: Define a new private exception type, please.
    # # If this attribute is *NOT* callable, raise an exception.
    # if not callable(beartypehintable_reducer):
    #     raise SomeExceptiot(...)
    # # Else, this attribute is callable.

    # Replace this hint with the new type hint returned by this callable.
    hint = __beartype_hint__()

    if hints_parent_beartypehintable is None:
        hints_parent_beartypehintable = frozenset((hint,))
    else:
        #FIXME: Unsure if this works for frozensets. Probably not. *sigh*
        hints_parent_beartypehintable |= {hint,}

    # Return this transformed hint.
    return (hint, hints_parent_beartypehintable)
