#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class testers** (i.e., low-level callables testing and validating
various properties of arbitrary classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype._cave._cavefast import TestableTypes as TestableTypesTuple
from beartype._data.cls.datacls import (
    TYPES_BUILTIN_FAKE,
    TYPE_BUILTIN_FAKE_PYCAPSULE_NAME,
)
from beartype._data.module.datamodpy import BUILTINS_MODULE_NAME
from beartype._data.hint.datahinttyping import (
    TypeException,
    TypeOrTupleTypes,
)
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ RAISERS                            }....................
def die_unless_type(
    # Mandatory parameters.
    cls: object,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilTypeException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is a class.

    Parameters
    ----------
    cls : object
        Object to be validated.
    exception_cls : Type[Exception]
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilTypeException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    exception_cls
        If this object is *not* a class.
    '''

    # If this object is *NOT* a class, raise an exception.
    if not isinstance(cls, type):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            'f{repr(exception_prefix)} not string.')

        raise exception_cls(f'{exception_prefix}{repr(cls)} not class.')
    # Else, this object is a class.


#FIXME: Unit test us up.
def die_unless_type_or_types(
    # Mandatory parameters.
    type_or_types: object,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilTypeException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is either a
    class *or* tuple of one or more classes.

    Parameters
    ----------
    type_or_types : object
        Object to be validated.
    exception_cls : Type[Exception]
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilTypeException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    exception_cls
        If this object is neither a class *nor* tuple of one or more classes.
    '''

    # If this object is neither a class *NOR* tuple of one or more classes,
    # raise an exception.
    if not is_type_or_types(type_or_types):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Exception message to be raised below.
        exception_message = (
            f'{exception_prefix}{repr(type_or_types)} neither '
            f'class nor tuple of one or more classes'
        )

        # If this object is a tuple...
        if isinstance(type_or_types, tuple):
            # If this tuple is empty, note that.
            if not type_or_types:
                exception_message += ' (i.e., is empty tuple)'
            # Else, this tuple is non-empty. In this case...
            else:
                # For the 0-based index of each tuple item and that item...
                for cls_index, cls in enumerate(type_or_types):
                    # If this object is *NOT* a class...
                    if not isinstance(cls, type):
                        # Note this.
                        exception_message += (
                            f' (i.e., tuple item {cls_index} '
                            f'{repr(cls)} not class)'
                        )

                        # Halt iteration.
                        break
                    # Else, this object is a class. Continue to the next item.
        # Else, this object is a non-tuple. In this case, the general-purpose
        # exception message suffices.

        # Raise this exception.
        raise exception_cls(f'{exception_message}.')
    # Else, this object is either a class *OR* tuple of one or more classes.

# ....................{ TESTERS                            }....................
def is_type_or_types(type_or_types: object) -> bool:
    '''
    :data:`True` only if the passed object is either a class *or* tuple of one
    or more classes.

    Parameters
    ----------
    type_or_types : object
        Object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this object is either a class *or* tuple of one or
        more classes.
    '''

    # Return true only if either...
    return (
        # This object is a class *OR*...
        isinstance(type_or_types, type) or
        (
            # This object is a tuple *AND*...
            isinstance(type_or_types, tuple) and
            # This tuple is non-empty *AND*...
            bool(type_or_types) and
            # This tuple contains only classes.
            all(isinstance(cls, type) for cls in type_or_types)
        )
    )

# ....................{ TESTERS ~ builtin                  }....................
@callable_cached
def is_type_builtin(cls: type) -> bool:
    '''
    :data:`True` only if the passed class is **builtin** (i.e., a globally
    accessible C-based type requiring *no* explicit importation).

    Note that this tester intentionally ignores **fake builtin types** (i.e.,
    types that are *not* builtin but nonetheless erroneously masquerade as being
    builtin, which includes the type of the :data:`None` singleton) by returning
    :data:`False` when passed a fake builtin type. If this is undesirable,
    consider calling the lower-level :func:`is_type_builtin_or_fake` tester.

    This tester is memoized for efficiency.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this class is builtin.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # This return true only if...
    return (
        # This is a possibly fake builtin type *AND*...
        is_type_builtin_or_fake(cls) and
        # This type is *NOT* a fake builtin. Specifically, neither...
        not (
            # This type is a non-PyCapsule fake builtin *NOR*...
            cls in TYPES_BUILTIN_FAKE or
            # This type is the PyCapsule fake builtin. See the docstring of this
            # global for further commentary. There be bugbears here.
            cls.__name__ == TYPE_BUILTIN_FAKE_PYCAPSULE_NAME
        # Then this type is a fake builtin. In this case, reject this type.
        )
    )


def is_type_builtin_or_fake(cls: type) -> bool:
    '''
    :data:`True` only if the passed class is a **possibly fake builtin** (i.e.,
    a type declared by the standard :mod:`builtins` module).

    Note that this tester intentionally accepts **fake builtin types** (i.e.,
    types that are *not* builtin but nonetheless erroneously masquerade as being
    builtin, which includes the type of the :data:`None` singleton) by returning
    :data:`True` when passed a fake builtin type. If this is undesirable,
    consider calling the higher-level :func:`is_type_builtin` tester.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this class is builtin.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import (
        get_object_type_module_name_or_none)

    # If this object is *NOT* a type, raise an exception.
    die_unless_type(cls)
    # Else, this object is a type.

    # Fully-qualified name of the module defining this type if this type is
    # defined by a module *OR* "None" otherwise (i.e., if this type is
    # dynamically defined in-memory).
    cls_module_name = get_object_type_module_name_or_none(cls)

    # This return true only if this name is that of the "builtins" module
    # declaring all builtin types.
    return cls_module_name == BUILTINS_MODULE_NAME

# ....................{ TESTERS ~ subclass                 }....................
def is_type_subclass(
    cls: object, base_classes: TypeOrTupleTypes) -> bool:
    '''
    :data:`True` only if the passed object is an inclusive subclass of the
    passed superclass(es).

    Specifically, this tester returns :data:`True` only if either:

    * If ``base_classes`` is a single superclass, the passed class is either:

      * That superclass itself *or*...
      * A subclass of that superclass.

    * Else, ``base_classes`` is a tuple of one or more superclasses. In this
      case, the passed class is either:

      * One of those superclasses themselves *or*...
      * A subclass of one of those superclasses.

    Caveats
    ----------
    **This higher-level tester should always be called in lieu of the
    lower-level** :func:`issubclass` **builtin,** which raises an undescriptive
    exception when the first passed parameter is *not* a class: e.g.,

    .. code-block:: python

       >>> issubclass(object(), type)
       TypeError: issubclass() arg 1 must be a class

    This tester suffers no such deficits, instead safely returning ``False``
    when the first passed parameter is *not* a class.

    Parameters
    ----------
    obj : object
        Object to be inspected.
    base_classes : TestableTypes
        Superclass(es) to test whether this object is a subclass of defined as
        either:

        * A single class.
        * A tuple of one or more classes.

    Returns
    ----------
    bool
        :data:`True` only if this object is an inclusive subclass of these
        superclass(es).
    '''
    assert isinstance(base_classes, TestableTypesTuple), (
        f'{repr(base_classes)} neither class nor tuple of classes.')

    # Return true only if...
    return (
        # This object is a class *AND*...
        isinstance(cls, type) and
        # This class either is this superclass(es) or a subclass of this
        # superclass(es).
        issubclass(cls, base_classes)
    )


#FIXME: Unit test us up, please.
def is_type_subclass_proper(
    cls: object, base_classes: TypeOrTupleTypes) -> bool:
    '''
    ``True`` only if the passed object is a proper subclass of the passed
    superclass(es).

    Specifically, this tester returns ``True`` only if either:

    * If ``base_classes`` is a single superclass, the passed class is a subclass
      of that superclass (but *not* that superclass itself).
    * Else, ``base_classes`` is a tuple of one or more superclasses. In this
      case, the passed class is a subclass of one of those superclasses (but
      *not* one of those superclasses themselves).

    Parameters
    ----------
    obj : object
        Object to be inspected.
    base_classes : TestableTypes
        Superclass(es) to test whether this object is a subclass of defined as
        either:

        * A single class.
        * A tuple of one or more classes.

    Returns
    ----------
    bool
        ``True`` only if this object is a proper subclass of these
        superclass(es).
    '''
    assert isinstance(base_classes, TestableTypesTuple), (
        f'{repr(base_classes)} neither class nor tuple of classes.')

    # Return true only if...
    return (
        # This object is a class *AND*...
        isinstance(cls, type) and
        # This class either is this superclass(es) or a subclass of this
        # superclass(es) *AND*...
        issubclass(cls, base_classes) and
        # It is *NOT* the case that...
        not (
            # If the caller passed a tuple of one or more superclasses, this
            # class is one of these superclasses themselves;
            cls in base_classes
            if isinstance(base_classes, tuple) else
            # Else, the caller passed a single superclass. In this case, this
            # class is this superclass itself.
            cls is base_classes
        )
    )
