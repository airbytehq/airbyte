#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **forward reference type hint
utilities** (i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant forward reference type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import Union
from beartype._data.hint.datahinttyping import TypeException
from beartype._util.cls.utilclstest import die_unless_type
from beartype._util.hint.pep.proposal.pep484.utilpep484ref import (
    HINT_PEP484_FORWARDREF_TYPE,
    get_hint_pep484_forwardref_type_basename,
    is_hint_pep484_forwardref,
)
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.module.utilmodimport import import_module_attr

# ....................{ HINTS                              }....................
#FIXME: Shift into "datatyping", please. When doing so, note that
#"HINT_PEP484_FORWARDREF_TYPE" should be shifted as well. :}
HINT_PEP484585_FORWARDREF_TYPES = (str, HINT_PEP484_FORWARDREF_TYPE)
'''
Tuple union of all :pep:`484`- or :pep:`585`-compliant **forward reference
types** (i.e., classes of all forward reference objects).

Specifically, this union contains:

* :class:`str`, the class of all :pep:`585`-compliant forward reference objects
  implicitly preserved by all :pep:`585`-compliant type hint factories when
  subscripted by a string.
* :class:`HINT_PEP484_FORWARDREF_TYPE`, the class of all :pep:`484`-compliant
  forward reference objects implicitly created by all :mod:`typing` type hint
  factories when subscripted by a string.

While :pep:`585`-compliant type hint factories preserve string-based forward
references as is, :mod:`typing` type hint factories coerce string-based forward
references into higher-level objects encapsulating those strings. The latter
approach is the demonstrably wrong approach, because encapsulating strings only
harms space and time complexity at runtime with *no* concomitant benefits.
'''


#FIXME: Shift into "datatyping", please.
Pep484585ForwardRef = Union[str, HINT_PEP484_FORWARDREF_TYPE]
'''
Union of all :pep:`484`- or :pep:`585`-compliant **forward reference types**
(i.e., classes of all forward reference objects).

See Also
----------
:data`HINT_PEP484585_FORWARDREF_TYPES`
    Further details.
'''

# ....................{ VALIDATORS                         }....................
def die_unless_hint_pep484585_forwardref(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **forward reference type hint** (i.e., object
    referring to a user-defined class that typically has yet to be defined).

    Equivalently, this validator raises an exception if this object is neither:

    * A string whose value is the syntactically valid name of a class.
    * An instance of the :class:`typing.ForwardRef` class. The :mod:`typing`
      module implicitly replaces all strings subscripting :mod:`typing` objects
      (e.g., the ``MuhType`` in ``List['MuhType']``) with
      :class:`typing.ForwardRef` instances containing those strings as instance
      variables, for nebulous reasons that make little justifiable sense but
      what you gonna do 'cause this is 2020. *Fight me.*

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this object is *not* a forward reference type hint.
    '''

    # If this object is *NOT* a forward reference type hint, raise an exception.
    if not isinstance(hint, HINT_PEP484585_FORWARDREF_TYPES):
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise BeartypeDecorHintForwardRefException(
            f'{exception_prefix}type hint {repr(hint)} not forward reference '
            f'(i.e., neither string nor "typing.ForwardRef" instance).'
        )
    # Else, this object is a forward reference type hint.

# ....................{ GETTERS ~ kind : forwardref        }....................
#FIXME: Unit test against nested classes.
#FIXME: Validate that this forward reference string is *NOT* the empty string.
#FIXME: Validate that this forward reference string is a syntactically valid
#"."-delimited concatenation of Python identifiers. We already have logic
#performing that validation somewhere, so let's reuse that here, please.
#Right. So, we already have an is_identifier() tester; now, we just need to
#define a new die_unless_identifier() validator.
def get_hint_pep484585_forwardref_classname(
    hint: Pep484585ForwardRef) -> str:
    '''
    Possibly unqualified classname referred to by the passed :pep:`484`- or
    :pep:`585`-compliant **forward reference type hint** (i.e., object
    indirectly referring to a user-defined class that typically has yet to be
    defined).

    Specifically, this function returns:

    * If this hint is a :pep:`484`-compliant forward reference (i.e., instance
      of the :class:`typing.ForwardRef` class), the typically unqualified
      classname referred to by that reference. Although :pep:`484` only
      explicitly supports unqualified classnames as forward references, the
      :class:`typing.ForwardRef` class imposes *no* runtime constraints and
      thus implicitly supports both qualified and unqualified classnames.
    * If this hint is a :pep:`585`-compliant forward reference (i.e., string),
      this string as is referring to a possibly unqualified classname. Both
      :pep:`585` and :mod:`beartype` itself impose *no* runtime constraints and
      thus explicitly support both qualified and unqualified classnames.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be inspected.

    Returns
    ----------
    str
        Possibly unqualified classname referred to by this forward reference.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.

    See Also
    ----------
    :func:`get_hint_pep484585_forwardref_classname_relative_to_object`
        Getter returning fully-qualified forward reference classnames.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    die_unless_hint_pep484585_forwardref(hint)

    # Return either...
    return (
        # If this hint is a PEP 484-compliant forward reference, the typically
        # unqualified classname referred to by this reference.
        get_hint_pep484_forwardref_type_basename(hint)  # type: ignore[return-value]
        if is_hint_pep484_forwardref(hint) else
        # Else, this hint is a string. In this case, this string as is.
        hint
    )


#FIXME: Unit test against nested classes.
def get_hint_pep484585_forwardref_classname_relative_to_object(
    hint: Pep484585ForwardRef, obj: object) -> str:
    '''
    Fully-qualified classname referred to by the passed **forward reference
    type hint** (i.e., object indirectly referring to a user-defined class that
    typically has yet to be defined) canonicalized if this hint is unqualified
    relative to the module declaring the passed object (e.g., callable, class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation mostly reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be canonicalized.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).

    Returns
    ----------
    str
        Fully-qualified classname referred to by this forward reference
        relative to this callable.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If either:

        * This forward reference is *not* actually a forward reference.
        * This forward reference is **relative** (i.e., contains *no* ``.``
          delimiters) and the passed ``obj`` does *not* define the
          ``__module__`` dunder instance variable.

    See Also
    ----------
    :func:`get_hint_pep484585_forwardref_classname`
        Getter returning possibly unqualified forward reference classnames.
    '''

    # Possibly unqualified classname referred to by this forward reference.
    forwardref_classname = get_hint_pep484585_forwardref_classname(hint)

    # If this classname contains one or more "." characters and is thus already
    # (...hopefully) fully-qualified, return this classname as is.
    if '.' in forwardref_classname:
        return forwardref_classname
    # Else, this classname contains *NO* "." characters and is thus *NOT*
    # fully-qualified.

    # Fully-qualified name of the module declaring the passed object if any *OR*
    # "None" otherwise.
    #
    # Note that, although *ALL* objects should define the "__module__" instance
    # variable underlying the call to this getter function, *SOME* real-world
    # objects do not. For this reason, we intentionally call the
    # get_object_module_name_or_none() rather than get_object_module_name()
    # function, explicitly detect "None", and raise a human-readable exception;
    # doing so produces significantly more readable exceptions than merely
    # calling get_object_module_name(). Problematic objects include:
    # * Objects defined in Sphinx-specific "conf.py" configuration files. In
    #   all likelihood, Sphinx is running these files in some sort of arcane and
    #   non-standard manner (over which we have *NO* control).
    obj_module_name = get_object_module_name_or_none(obj)

    # If this object is declared by a module, canonicalize the name of this
    # reference by returning the "."-delimited concatenation of the
    # fully-qualified name of this module with this unqualified classname.
    if obj_module_name:
        return f'{get_object_module_name_or_none(obj)}.{forwardref_classname}'
    # Else, this object is *NOT* declared by a module.

    # Raise a human-readable exception. (See above.)
    raise BeartypeDecorHintForwardRefException(
        f'Relative forward reference "{forwardref_classname}" not '
        f'canonicalizeable against module-less {repr(obj)}.'
    )

# ....................{ IMPORTERS                          }....................
#FIXME: Unit test us up, please.
def import_pep484585_forwardref_type_relative_to_object(
    # Mandatory parameters.
    hint: Pep484585ForwardRef,
    obj: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> type:
    '''
    Class referred to by the passed :pep:`484` or :pep:`585`-compliant
    **forward reference type hint** (i.e., object indirectly referring to a
    user-defined class that typically has yet to be defined) canonicalized if
    this hint is unqualified relative to the module declaring the passed object
    (e.g., callable, class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the passed object is typically a
    :func:`beartype.beartype`-decorated callable passed exactly once to this
    function.

    Parameters
    ----------
    hint : Pep484585ForwardRef
        Forward reference type hint to be resolved.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintForwardRefException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    type
        Class referred to by this forward reference.

    Raises
    ----------
    :exc:`exception_cls`
        If the object referred to by this forward reference is either undefined
        *or* is defined but is not a class.
    '''

    # Human-readable label prefixing exception messages raised below.
    EXCEPTION_PREFIX = f'{exception_prefix}{repr(hint)} referenced class '

    # Fully-qualified classname referred to by this forward reference relative
    # to this object.
    hint_forwardref_classname = (
        get_hint_pep484585_forwardref_classname_relative_to_object(
            hint=hint, obj=obj))

    # Object dynamically imported from this classname.
    hint_forwardref_type = import_module_attr(
        module_attr_name=hint_forwardref_classname,
        exception_cls=exception_cls,
        exception_prefix=EXCEPTION_PREFIX,
    )

    # If this object is *NOT* a class, raise an exception.
    die_unless_type(
        cls=hint_forwardref_type,
        exception_cls=exception_cls,
        exception_prefix=EXCEPTION_PREFIX,
    )
    # Else, this object is a class.

    # Return this class.
    return hint_forwardref_type
