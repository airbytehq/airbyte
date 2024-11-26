#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Unmemoized beartype decorators** (i.e., core lower-level unmemoized decorators
underlying the higher-level memoized :func:`beartype.beartype` decorator, whose
implementation in the parent :mod:`beartype._decor.decorcache` submodule
is a thin wrapper efficiently memoizing closures internally created and returned
by that decorator; in turn, those closures directly defer to this submodule).

This private submodule is effectively the :func:`beartype.beartype` decorator
despite *not* actually being that decorator (due to being unmemoized).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeException
from beartype._conf.confcls import BeartypeConf
from beartype._data.hint.datahinttyping import BeartypeableT
from beartype._decor._decornontype import beartype_nontype
from beartype._decor._decortype import beartype_type
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.text.utiltextlabel import label_object_context
from beartype._util.text.utiltextmunge import (
    truncate_str,
    uppercase_str_char_first,
)
from beartype._util.text.utiltextprefix import prefix_beartypeable
from traceback import format_exc
from warnings import warn

# ....................{ DECORATORS                         }....................
def beartype_object(
    # Mandatory parameters.
    obj: BeartypeableT,
    conf: BeartypeConf,

    # Variadic keyword parameters.
    **kwargs
) -> BeartypeableT:
    '''
    Decorate the passed **beartypeable** (i.e., caller-defined object that may
    be decorated by the :func:`beartype.beartype` decorator) with optimal
    type-checking dynamically generated unique to that beartypeable.

    Parameters
    ----------
    obj : BeartypeableT
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.
    conf : BeartypeConf
        **Beartype configuration** (i.e., dataclass encapsulating all flags,
        options, settings, and other metadata configuring the current decoration
        of the decorated callable or class).

    All remaining keyword parameters are passed as is to whichever lower-level
    decorator this higher-level decorator calls on the passed beartypeable.

    Returns
    ----------
    BeartypeableT
        Either:

        * If the passed object is a class, this existing class embellished with
          dynamically generated type-checking.
        * If the passed object is a callable, a new callable wrapping that
          callable with dynamically generated type-checking.

    See Also
    ----------
    :func:`beartype._decor.decormain.beartype`
        Memoized parent decorator wrapping this unmemoized child decorator.
    '''
    # print(f'Decorating object {repr(obj)}...')

    # Return either...
    return (
        _beartype_object_fatal(obj, conf=conf, **kwargs)
        # If this beartype configuration requests that this decorator raise
        # fatal exceptions at decoration time, defer to the lower-level
        # decorator doing so;
        if conf.warning_cls_on_decorator_exception is None else
        # Else, this beartype configuration requests that this decorator emit
        # fatal warnings at decoration time. In this case, defer to the
        # lower-level decorator doing so.
        _beartype_object_nonfatal(obj, conf=conf, **kwargs)
    )

# ....................{ PRIVATE ~ decorators               }....................
def _beartype_object_fatal(obj: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Decorate the passed **beartypeable** (i.e., caller-defined object that may
    be decorated by the :func:`beartype.beartype` decorator) with optimal
    type-checking dynamically generated unique to that beartypeable.

    Parameters
    ----------
    obj : BeartypeableT
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.

    All remaining keyword parameters are passed as is to a lower-level decorator
    defined by this submodule (e.g., :func:`.beartype_func`).

    Returns
    ----------
    BeartypeableT
        Either:

        * If the passed object is a class, this existing class embellished with
          dynamically generated type-checking.
        * If the passed object is a callable, a new callable wrapping that
          callable with dynamically generated type-checking.

    See Also
    ----------
    :func:`beartype._decor.decormain.beartype`
        Memoized parent decorator wrapping this unmemoized child decorator.
    '''

    # Return either...
    return (
        # If this object is a class, this class decorated with type-checking.
        beartype_type(obj, **kwargs)  # type: ignore[return-value]
        if isinstance(obj, type) else
        # Else, this object is a non-class. In this case, this non-class
        # decorated with type-checking.
        beartype_nontype(obj, **kwargs)  # type: ignore[return-value]
    )


#FIXME: Unit test us up, please.
def _beartype_object_nonfatal(
    # Mandatory parameters.
    obj: BeartypeableT,
    conf: BeartypeConf,

    # Variadic keyword parameters.
    **kwargs
) -> BeartypeableT:
    '''
    Decorate the passed **beartypeable** (i.e., pure-Python callable or class)
    with optimal type-checking dynamically generated unique to that
    beartypeable and any otherwise uncaught exception raised by doing so safely
    coerced into a warning instead.

    Motivation
    ----------
    This decorator is principally intended to be called by our **import hook
    API** (i.e., public functions exported by the :mod:`beartype.claw`
    subpackage). Raising detailed exception tracebacks on unexpected error
    conditions is:

    * The right thing to do for callables and classes manually type-checked with
      the :func:`beartype.beartype` decorator.
    * The wrong thing to do for callables and classes automatically type-checked
      by import hooks installed by public functions exported by the
      :mod:`beartype.claw` subpackage. Why? Because doing so would render those
      import hooks fragile to the point of being practically useless on
      real-world packages and codebases by unexpectedly failing on the first
      callable or class defined *anywhere* under a package that is not
      type-checkable by :func:`beartype.beartype` (whether through our fault or
      that package's). Instead, the right thing to do is to:

      * Emit a warning for each callable or class that :func:`beartype.beartype`
        fails to generate a type-checking wrapper for.
      * Continue to the next callable or class.

    Parameters
    ----------
    obj : BeartypeableT
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.
    conf : BeartypeConf
        **Beartype configuration** (i.e., dataclass encapsulating all flags,
        options, settings, and other metadata configuring the current decoration
        of the decorated callable or class).

    All remaining keyword parameters are passed as is to the lower-level
    :func:`._beartype_object_fatal` decorator internally called by this
    higher-level decorator on the passed beartypeable.

    Returns
    ----------
    BeartypeableT
        Either:

        * If :func:`.beartype_object_fatal` raises an exception, the passed
          object unmodified as is.
        * If :func:`.beartype_object_fatal` raises no exception:

          * If the passed object is a class, this existing class embellished with
            dynamically generated type-checking.
          * If the passed object is a callable, a new callable wrapping that
            callable with dynamically generated type-checking.

    Warns
    ----------
    warning_category
        If :func:`.beartype_object_fatal` fails to generate a type-checking
        wrapper for this callable or class by raising a fatal exception, this
        decorator coerces that exception into a non-fatal warning instead.
    '''

    # Attempt to decorate the passed beartypeable.
    try:
        return _beartype_object_fatal(obj, conf=conf, **kwargs)
    # If doing so unexpectedly raises an exception, coerce that fatal exception
    # into a non-fatal warning for nebulous safety.
    except Exception as exception:
        # Category of warning to be emitted.
        warning_category = conf.warning_cls_on_decorator_exception
        assert is_type_subclass(warning_category, Warning), (
            f'{repr(warning_category)} not warning category.')

        # Original error message to be embedded in the warning message to be
        # emitted, stripped of *ALL* ANSI color. While colors improve the
        # readability of exception messages that percolate down to an ANSI-aware
        # command line, warnings are usually harvested and then regurgitated by
        # intermediary packages into ANSI-unaware logfiles.
        #
        # This message is defined as either...
        error_message = (
            # If this exception is beartype-specific, this exception's message
            # is probably human-readable as is. In this case, maximize brevity
            # and readability by coercing *ONLY* this message (rather than both
            # this message *AND* traceback) truncated to a reasonable maximum
            # length into a warning message.
            truncate_str(text=str(exception), max_len=1024)
            if isinstance(exception, BeartypeException) else
            # Else, this exception is *NOT* beartype-specific. In this case,
            # this exception's message is probably *NOT* human-readable as is.
            # Prepend that non-human-readable message by this exception's
            # traceback for disambiguity and debuggability. Note that the
            # format_exc() function appends this exception's message to this
            # traceback and thus suffices as is.
            format_exc()
        )

        # Indent this exception message by globally replacing *EVERY* newline in
        # this message with a newline followed by four spaces. Doing so visually
        # offsets this lower-level exception message from the higher-level
        # warning message embedding this exception message below.
        error_message = error_message.replace('\n', '\n    ')

        # Warning message to be emitted, consisting of:
        # * A human-readable label contextually describing this beartypeable,
        #   capitalized such that the first character is uppercase.
        # * This indented exception message.
        warning_message = uppercase_str_char_first(
            f'{prefix_beartypeable(obj)}{label_object_context(obj)}:\n'
            f'{error_message}'
        )

        # Emit this message under this category.
        warn(warning_message, warning_category)

    # Return this object unmodified, as @beartype failed to successfully wrap
    # this object with a type-checking class or callable. So it goes, fam.
    return obj  # type: ignore[return-value]
