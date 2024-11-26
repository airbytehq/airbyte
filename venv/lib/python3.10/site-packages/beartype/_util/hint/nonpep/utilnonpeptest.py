#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-noncompliant type hint tester** (i.e., callable validating an
arbitrary object to be a PEP-noncompliant type hint) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Validate strings to be syntactically valid classnames via a globally
#scoped compiled regular expression. Raising early exceptions at decoration
#time is preferable to raising late exceptions at call time.
#FIXME: Indeed, we now provide such a callable:
#    from beartype._util.module.utilmodget import die_unless_module_attr_name

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintNonpepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_type_isinstanceable,
    is_type_or_types_isinstanceable,
)
from beartype._data.hint.datahinttyping import TypeException

# ....................{ VALIDATORS                         }....................
#FIXME: Unit test us up, please.
def die_if_hint_nonpep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = True,
    exception_cls: TypeException = BeartypeDecorHintNonpepException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception if the passed object is a **PEP-noncompliant type hint**
    (i.e., :mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    is_str_valid : bool, optional
        ``True`` only if this function permits this object to either be a
        string or contain strings. Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class
          or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.
    exception_cls : type[Exception]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintNonpepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
        If this object is either:

        * An **isinstanceable type** (i.e., standard class passable as the
          second parameter to the :func:`isinstance` builtin and thus typically
          *not* compliant with annotation-centric PEPs).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''

    # If this object is a PEP-noncompliant type hint, raise an exception.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if is_hint_nonpep(hint, is_str_valid):
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception type.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'is PEP-noncompliant (e.g., neither ' +
            (
                (
                    'isinstanceable class, forward reference, nor tuple of '
                    'isinstanceable classes and/or forward references).'
                )
                if is_str_valid else
                'isinstanceable class nor tuple of isinstanceable classes).'
            )
        )
    # Else, this object is *NOT* a PEP-noncompliant type hint.


#FIXME: Unit test this function with respect to non-isinstanceable classes.
def die_unless_hint_nonpep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = True,
    exception_cls: TypeException = BeartypeDecorHintNonpepException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-noncompliant type
    hint** (i.e., :mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    is_str_valid : bool, optional
        ``True`` only if this function permits this object to either be a
        string or contain strings. Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class
          or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.
    exception_cls : type[Exception], optional
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintNonpepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
        If this object is neither:

        * An **isinstanceable type** (i.e., standard class passable as the
          second parameter to the :func:`isinstance` builtin and thus typically
          *not* compliant with annotation-centric PEPs).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''

    # If this object is a PEP-noncompliant type hint, reduce to a noop.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if is_hint_nonpep(hint, is_str_valid):
        return
    # Else, this object is *NOT* a PEP-noncompliant type hint. In this case,
    # subsequent logic raises an exception specific to the passed parameters.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with the is_hint_nonpep() tester below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not type.')
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # If this object is a class...
    if isinstance(hint, type):
        # If this class is *NOT* PEP-noncompliant, raise an exception.
        die_unless_hint_nonpep_type(
            hint=hint,
            exception_prefix=exception_prefix,
            exception_cls=exception_cls,
        )

        # Else, this class is isinstanceable. In this case, silently accept
        # this class as is.
        return
    # Else, this object is *NOT* a class.
    #
    # If this object is a tuple, raise a tuple-specific exception.
    elif isinstance(hint, tuple):
        die_unless_hint_nonpep_tuple(
            hint=hint,
            exception_prefix=exception_prefix,
            is_str_valid=is_str_valid,
            exception_cls=exception_cls,
        )
    # Else, this object is neither a type nor type tuple.

    # Raise a generic exception.
    raise exception_cls(
        f'{exception_prefix}type hint {repr(hint)} either '
        f'PEP-noncompliant or currently unsupported by @beartype.'
    )

    #FIXME: Temporarily preserved in case we want to restore this. *shrug*
    # # Else, this object is neither a forward reference, class, nor tuple. Ergo,
    # # this object is *NOT* a PEP-noncompliant type hint.
    # #
    # # If forward references are supported, raise an exception noting that.
    # elif is_str_valid:
    #     raise exception_cls(
    #         f'{exception_prefix}type hint {repr(hint)} '
    #         f'neither PEP-compliant nor -noncompliant '
    #         f'(e.g., neither PEP-compliant, isinstanceable class, forward reference, or '
    #         f'tuple of isinstanceable classes and forward references).'
    #     )
    # # Else, forward references are unsupported. In this case, raise an
    # # exception noting that.
    # else:
    #     raise exception_cls(
    #         f'{exception_prefix}type hint {repr(hint)} '
    #         f'neither PEP-compliant nor -noncompliant '
    #         f'(e.g., isinstanceable class or tuple of isinstanceable classes).'
    #     )

# ....................{ VALIDATORS ~ kind                  }....................
#FIXME: Unit test us up.
def die_unless_hint_nonpep_type(
    # Mandatory parameters.
    hint: type,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintNonpepException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is an **isinstanceable type**
    (i.e., standard class passable as the second parameter to the
    :func:`isinstance` builtin and thus typically *not* compliant with
    annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : type
        Object to be validated.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintNonpepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    BeartypeDecorHintPep3119Exception
        If this object is *not* an isinstanceable class (i.e., class passable
        as the second argument to the :func:`isinstance` builtin).
    :exc:`exception_cls`
        If this object is a PEP-compliant type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpeptest import die_if_hint_pep

    # If this object is a PEP-compliant type hint, raise an exception.
    die_if_hint_pep(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is *NOT* a PEP-noncompliant type hint.
    #
    # If this object is *NOT* an isinstanceable class, raise an exception. Note
    # that this validation is typically slower than the prior validation and
    # thus intentionally performed last.
    die_unless_type_isinstanceable(
        cls=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # If this object is an isinstanceable class.


#FIXME: Unit test this function with respect to tuples containing
#non-isinstanceable classes.
#FIXME: Optimize both this and the related _is_hint_nonpep_tuple() tester
#defined below. The key realization here is that EAFP is *MUCH* faster in this
#specific case than iteration. Why? Because iteration is guaranteed to
#internally raise a stop iteration exception, whereas EAFP only raises an
#exception if this tuple is invalid, in which case efficiency is no longer a
#concern. So, what do we do instead? Simple. We internally refactor:
#* If "is_str_valid" is True, we continue to perform the existing
#  implementation of both functions. *shrug*
#* Else, we:
#  * Perform a new optimized EAFP-style isinstance() check resembling that
#    performed by die_unless_type_isinstanceable().
#  * Likewise for _is_hint_nonpep_tuple() vis-a-vis is_type_or_types_isinstanceable().
#Fortunately, tuple unions are now sufficiently rare in the wild (i.e., in
#real-world use cases) that this mild inefficiency probably no longer matters.
#FIXME: Indeed! Now that we have the die_unless_type_or_types_isinstanceable()
#validator, this validator should reduce to efficiently calling
#die_unless_type_or_types_isinstanceable() directly if "is_str_valid" is False.
#die_unless_type_or_types_isinstanceable() performs the desired EAFP-style
#isinstance() check in an optimally efficient manner.
def die_unless_hint_nonpep_tuple(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = False,
    exception_cls: TypeException = BeartypeDecorHintNonpepException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-noncompliant tuple**
    (i.e., :mod:`beartype`-specific tuple of one or more PEP-noncompliant types
    *not* compliant with annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    is_str_valid : bool, optional
        ``True`` only if this function permits this tuple to contain strings.
        Defaults to ``False``. If:

        * ``True``, this tuple is valid only when containing classes and/or
          classnames.
        * ``False``, this tuple is valid only when containing classes.
    exception_cls : type, optional
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintNonpepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
        If this object is neither:

        * A non-:mod:`typing` type (i.e., class *not* defined by the
          :mod:`typing` module, whose public classes are used to instantiate
          PEP-compliant type hints or objects satisfying such hints that
          typically violate standard class semantics and thus require
          PEP-specific handling).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''

    # If this object is a tuple union, reduce to a noop.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if _is_hint_nonpep_tuple(hint, is_str_valid):
        return
    # Else, this object is *NOT* a tuple union. In this case, subsequent logic
    # raises an exception specific to the passed parameters.
    #
    # Note that the prior call has already validated "is_str_valid".
    assert isinstance(exception_cls, type), f'{repr(exception_cls)} not type.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with the _is_hint_nonpep_tuple() tester.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this object is *NOT* a tuple, raise an exception.
    if not isinstance(hint, tuple):
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not tuple.')
    # Else, this object is a tuple.
    #
    # If this tuple is empty, raise an exception.
    elif not hint:
        raise exception_cls(f'{exception_prefix}tuple type hint empty.')
    # Else, this tuple is non-empty.

    # For each item of this tuple...
    for hint_item in hint:
        # Duplicate the above logic. For negligible efficiency gains (and more
        # importantly to avoid exhausting the stack), avoid calling this
        # function recursively to do so. *shrug*

        # If this item is a class...
        if isinstance(hint_item, type):
            # If this class is *NOT* isinstanceable, raise an exception.
            die_unless_type_isinstanceable(
                cls=hint_item,
                exception_prefix=exception_prefix,
                exception_cls=exception_cls,
            )
        # Else, this item is *NOT* a class.
        #
        # If this item is a forward reference...
        elif isinstance(hint_item, str):
            # If forward references are unsupported, raise an exception.
            if not is_str_valid:
                raise exception_cls(
                    f'{exception_prefix}tuple type hint {repr(hint)} '
                    f'forward reference "{hint_item}" unsupported.'
                )
            # Else, silently accept this item.
        # Else, this item is neither a class nor forward reference. Ergo,
        # this item is *NOT* a PEP-noncompliant type hint. In this case,
        # raise an exception whose message contextually depends on whether
        # forward references are permitted or not.
        else:
            raise exception_cls(
                f'{exception_prefix}tuple type hint {repr(hint)} '
                f'item {repr(hint_item)} invalid '
                f'{"neither type nor string" if is_str_valid else "not type"}.'
            )

# ....................{ TESTERS                            }....................
def is_hint_nonpep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = False,
) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-noncompliant type hint**
    (i.e., :mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    is_str_valid : bool, optional
        ``True`` only if this function permits this object to be a string.
        Defaults to ``False``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class
          or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.

    Returns
    ----------
    bool
        ``True`` only if this object is either:

        * A non-:mod:`typing` type (i.e., class *not* defined by the
          :mod:`typing` module, whose public classes are used to instantiate
          PEP-compliant type hints or objects satisfying such hints that
          typically violate standard class semantics and thus require
          PEP-specific handling).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''
    assert isinstance(is_str_valid, bool), f'{repr(is_str_valid)} not boolean.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_nonpep() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Return true only if either...
    return (
        # If this object is a class, return true only if this is *NOT* a
        # PEP-compliant class, in which case this *MUST* be a PEP-noncompliant
        # class by definition.
        _is_hint_nonpep_type(hint) if isinstance(hint, type) else
        # Else, this object is *NOT* a class.
        #
        # If this object is a tuple, return true only if this tuple contains
        # only one or more caller-permitted forward references and
        # PEP-noncompliant classes.
        _is_hint_nonpep_tuple(hint, is_str_valid) if isinstance(hint, tuple)
        # Else, this object is neither a class nor tuple. Return false, as this
        # object *CANNOT* be PEP-noncompliant.
        else False
    )

# ....................{ TESTERS ~ private                  }....................
@callable_cached
def _is_hint_nonpep_tuple(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = False,
) -> bool:
    '''
    ``True`` only if the passed object is a PEP-noncompliant non-empty tuple of
    one or more types.

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    is_str_valid : bool, optional
        ``True`` only if this function permits this tuple to contain strings.
        Defaults to ``False``. If this boolean is:

        * ``True``, this tuple is valid only when containing classes and/or
          classnames.
        * ``False``, this object is valid only when containing classes.

    Returns
    ----------
    bool
        ``True`` only if this object is a **non-empty tuple** (i.e., semantic
        union of types) containing one or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''
    assert isinstance(is_str_valid, bool), f'{repr(is_str_valid)} not boolean.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_nonpep() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Return true only if this object is...
    return (
        # A tuple *AND*...
        isinstance(hint, tuple) and
        # This tuple is non-empty *AND*...
        len(hint) > 0 and
        # Each item of this tuple is either a caller-permitted forward
        # reference *OR* an isinstanceable class.
        all(
            is_type_or_types_isinstanceable(hint_item) if isinstance(hint_item, type) else
            is_str_valid                               if isinstance(hint_item, str) else
            False
            for hint_item in hint
        )
    )


def _is_hint_nonpep_type(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a PEP-noncompliant type.

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
        ``True`` only if this object is a PEP-noncompliant type.
    '''
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_nonpep() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep

    # Return true only if this object is isinstanceable and *NOT* a
    # PEP-compliant class, in which case this *MUST* be a PEP-noncompliant
    # class by definition.
    return is_type_or_types_isinstanceable(hint) and not is_hint_pep(hint)
