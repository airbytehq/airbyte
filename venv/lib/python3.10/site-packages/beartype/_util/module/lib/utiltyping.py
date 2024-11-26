#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **typing module** utilities (i.e., callables dynamically testing
and importing attributes declared at module scope by either the standard
:mod:`typing` or third-party :mod:`typing_extensions` modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeModuleAttributeNotFoundWarning
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype.typing import (
    Any,
    Iterable,
    Union,
)
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.module.datamodtyping import TYPING_MODULE_NAMES
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.module.utilmodimport import import_module_attr_or_none
from collections.abc import Iterable as IterableABC
from warnings import warn

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_typing_attr(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
) -> bool:
    '''
    :data:`True` only if a **typing attribute** (i.e., object declared at module
    scope by either the :mod:`typing` or :mod:`typing_extensions` modules) with
    the passed unqualified name is importable from one or more of these
    modules.

    This function is effectively memoized for efficiency.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.

    Returns
    -------
    bool
        :data:`True` only if the :mod:`typing` or :mod:`typing_extensions`
        modules declare an attribute with this name.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`._BeartypeUtilModuleException`.

    Raises
    ------
    exception_cls
        If this name is syntactically invalid.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If any of these modules raise module-scoped exceptions at importation
        time. That said, the :mod:`typing` and :mod:`typing_extensions` modules
        are scrupulously tested and thus unlikely to raise such exceptions.
    '''

    # Return true only if an attribute with this name is importable from either
    # the "typing" *OR* "typing_extensions" modules.
    #
    # Note that positional rather than keyword arguments are intentionally
    # passed to optimize memoization efficiency.
    return import_typing_attr_or_none(
        typing_attr_basename, exception_cls) is not None

# ....................{ IMPORTERS                          }....................
def import_typing_attr(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of these modules *or* raise an exception
    otherwise (i.e., if this attribute is *not* importable from these modules).

    This function is effectively memoized for efficiency.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`._BeartypeUtilModuleException`.

    Returns
    -------
    object
        Attribute with this name dynamically imported from a typing module.

    Raises
    ------
    exception_cls
        If either:

        * This name is syntactically invalid.
        * Neither the :mod:`typing` nor :mod:`typing_extensions` modules
          declare an attribute with this name.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If any of these modules raise module-scoped exceptions at importation
        time. That said, the :mod:`typing` and :mod:`typing_extensions` modules
        are scrupulously tested and thus unlikely to raise such exceptions.

    See Also
    --------
    :func:`beartype._util.module.utilmodimport.import_module_typing_any_attr_or_none`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodtest import is_module

    # Attribute with this name imported from either the "typing" or
    # "typing_extensions" modules if one or more of these modules declare this
    # attribute *OR* "None" otherwise.
    #
    # Note that positional rather than keyword arguments are intentionally
    # passed to optimize memoization efficiency.
    typing_attr = import_typing_attr_or_none(
        typing_attr_basename, exception_cls)

    # If none of these modules declare this attribute...
    if typing_attr is None:
        # Substrings prefixing and suffixing exception messages raised below.
        EXCEPTION_PREFIX = (
            f'Typing attributes "typing.{typing_attr_basename}" and '
            f'"typing_extensions.{typing_attr_basename}" not found. '
        )
        EXCEPTION_SUFFIX = (
            'We apologize for the inconvenience and hope you had a '
            'great dev cycle flying with Air Beartype, '
            '"Your Grizzled Pal in the Friendly Skies."'
        )

        # If the "typing_extensions" module is importable, raise an
        # appropriate exception.
        if is_module('typing_extensions'):
            raise exception_cls(
                f'{EXCEPTION_PREFIX} Please either '
                f'(A) update the "typing_extensions" package or '
                f'(B) update to a newer Python version. {EXCEPTION_SUFFIX}'
            )
        # Else, the "typing_extensions" module is unimportable. In this
        # case, raise an appropriate exception.
        else:
            raise exception_cls(
                f'{EXCEPTION_PREFIX} Please either '
                f'(A) install the "typing_extensions" package or '
                f'(B) update to a newer Python version. {EXCEPTION_SUFFIX}'
            )
    # Else, one or more of these modules declare this attribute.

    # Return this attribute.
    return typing_attr


#FIXME: Unit test us up, please.
def import_typing_attr_or_none(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of these modules *or* :data:`None` otherwise
    otherwise (i.e., if this attribute is *not* importable from these modules).

    This function is effectively memoized for efficiency.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`._BeartypeUtilModuleException`.

    Returns
    -------
    object
        Attribute with this name dynamically imported from a typing module.

    Raises
    ------
    exception_cls
        If this name is syntactically invalid.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If any of these modules raise module-scoped exceptions at importation
        time. That said, the :mod:`typing` and :mod:`typing_extensions` modules
        are scrupulously tested and thus unlikely to raise exceptions.

    See Also
    --------
    :func:`import_typing_attr_or_fallback`
        Further details.
    '''

    # One-liners in the rear view mirror may be closer than they appear.
    #
    # Note that parameters are intentionally passed positionally rather than by
    # keyword for memoization efficiency.
    return import_typing_attr_or_fallback(
        typing_attr_basename, None, exception_cls)


#FIXME: Unit test us up, please.
#FIXME: Leverage above, please.
@callable_cached
def import_typing_attr_or_fallback(
    # Mandatory parameters.
    typing_attr_basename: str,
    fallback: object,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of these modules *or* the passed fallback
    otherwise otherwise (i.e., if this attribute is *not* importable from these
    modules).

    Specifically, this function (in order):

    #. If the official :mod:`typing` module bundled with the active Python
       interpreter declares that attribute, dynamically imports and returns
       that attribute from that module.
    #. Else if the third-party (albeit quasi-official) :mod:`typing_extensions`
       module requiring external installation under the active Python
       interpreter declares that attribute, dynamically imports and returns
       that attribute from that module.
    #. Else, returns the passed fallback value.

    This function is memoized for efficiency.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.
    fallback : object
        Arbitrary value to be returned as a last-ditch fallback if *no* typing
        module declares this attribute.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`._BeartypeUtilModuleException`.

    Returns
    -------
    object
        Attribute with this name dynamically imported from a typing module.

    Raises
    ------
    exception_cls
        If this name is syntactically invalid.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If any of these modules raise module-scoped exceptions at importation
        time. That said, the :mod:`typing` and :mod:`typing_extensions` modules
        are scrupulously tested and thus unlikely to raise exceptions.
    '''

    # Attribute with this name imported from the "typing" module if that module
    # declares this attribute *OR* "None" otherwise.
    typing_attr = import_module_attr_or_none(
        module_attr_name=f'typing.{typing_attr_basename}',
        exception_cls=exception_cls,
        exception_prefix='Typing attribute ',
    )

    # If the "typing" module does *NOT* declare this attribute...
    if typing_attr is None:
        # Attribute with this name imported from the "typing_extensions" module
        # if that module declares this attribute *OR* "None" otherwise.
        typing_attr = import_module_attr_or_none(
            module_attr_name=f'typing_extensions.{typing_attr_basename}',
            exception_cls=exception_cls,
            exception_prefix='Typing attribute ',
        )

        # If the "typing_extensions" module also does *NOT* declare this
        # attribute, fallback to the passed fallback value.
        if typing_attr is None:
            typing_attr = fallback
        # Else, the "typing_extensions" module declares this attribute.
    # Else, the "typing" module declares this attribute.

    # Return either this attribute if one or more of these modules declare this
    # attribute *OR* this fallback otherwise.
    return typing_attr

# ....................{ ITERATORS                          }....................
def iter_typing_attrs(
    # Mandatory parameters.
    typing_attr_basenames: Union[str, Iterable[str]],

    # Optional parameters.
    is_warn: bool = False,
    typing_module_names: Iterable[str] = TYPING_MODULE_NAMES,
) -> IterableABC:
    '''
    Generator iteratively yielding all attributes with the passed basename
    declared by the quasi-standard typing modules with the passed
    fully-qualified names, silently ignoring those modules failing to declare
    such an attribute.

    Attributes
    ----------
    typing_attr_basenames : Union[str, Iterable[str]]
        Either:

        * Unqualified name of the attribute to be dynamically imported from
          each typing module, in which case either:

          * If the currently iterated typing module defines this attribute,
            this generator yields this attribute imported from that module.
          * Else, this generator silently ignores that module.
        * Iterable of one or more such names, in which case either:

          * If the currently iterated typing module defines *all* attributes,
            this generator yields a tuple whose items are these attributes
            imported from that module (in the same order).
          * Else, this generator silently ignores that module.
    is_warn : bool
        :data:`True` only if emitting non-fatal warnings for typing modules
        failing to define all passed attributes. If ``typing_module_names`` is
        passed, this parameter should typically also be passed as :data:`True`
        for safety. Defaults to :data:`False`.
    typing_module_names: Iterable[str]
        Iterable of the fully-qualified names of all typing modules to
        dynamically import this attribute from. Defaults to
        :data:`TYPING_MODULE_NAMES`.

    Yields
    ------
    Union[object, Tuple[object]]
        Either:

        * If passed only an attribute basename, the attribute with that
          basename declared by each typing module.
        * If passed an iterable of one or more attribute basenames, a tuple
          whose items are the attributes with those basenames (in the same
          order) declared by each typing module.
    '''
    assert isinstance(is_warn, bool), f'{is_warn} not boolean.'
    assert isinstance(typing_attr_basenames, (str, IterableABC)), (
        f'{typing_attr_basenames} not string.')
    assert typing_attr_basenames, '"typing_attr_basenames" empty.'
    assert isinstance(typing_module_names, IterableABC), (
        f'{repr(typing_module_names)} not iterable.')
    assert typing_module_names, '"typing_module_names" empty.'
    assert all(
        isinstance(typing_module_name, str)
        for typing_module_name in typing_module_names
    ), f'One or more {typing_module_names} items not strings.'

    # If passed an attribute basename, pack this into a tuple containing only
    # this basename for ease of use.
    if isinstance(typing_attr_basenames, str):
        typing_attr_basenames = (typing_attr_basenames,)
    # Else, an iterable of attribute basenames was passed. In this case...
    else:
        assert all(
            isinstance(typing_attr_basename, str)
            for typing_attr_basename in typing_attr_basenames
        ), f'One or more {typing_attr_basenames} items not strings.'
    # In either case, this parameter is now a tuple of attribute basenames.

    # List of all imported attributes to be yielded from each iteration of the
    # generator implicitly returned by this generator function.
    typing_attrs: list = []

    # For the fully-qualified name of each quasi-standard typing module...
    for typing_module_name in typing_module_names:
        # Clear this list *BEFORE* appending to this list below.
        typing_attrs.clear()

        # For the basename of each attribute to be imported from that module...
        for typing_attr_basename in typing_attr_basenames:
            # Fully-qualified name of this attribute declared by that module.
            module_attr_name = f'{typing_module_name}.{typing_attr_basename}'

            # Attribute with this name dynamically imported from that module if
            # that module defines this attribute *OR* "None" otherwise.
            typing_attr = import_module_attr_or_none(
                module_attr_name=module_attr_name,
                exception_prefix=f'"{typing_module_name}" attribute ',
            )

            # If that module fails to define this attribute...
            if typing_attr is None:
                # If emitting non-fatal warnings, do so.
                if is_warn:
                    warn(
                        f'Ignoring undefined typing attribute '
                        f'"{module_attr_name}"...',
                        BeartypeModuleAttributeNotFoundWarning,
                    )
                # Else, silently reduce to a noop.

                # Continue to the next module.
                break
            # Else, that module declares this attribute.

            # Append this attribute to this list.
            typing_attrs.append(typing_attr)
        # If that module declares *ALL* attributes...
        else:
            # If exactly one attribute name was passed, yield this attribute
            # as is (*WITHOUT* packing this attribute into a tuple).
            if len(typing_attrs) == 1:
                yield typing_attrs[0]
            # Else, two or more attribute names were passed. In this case,
            # yield these attributes as a tuple.
            else:
                yield tuple(typing_attrs)
        # Else, that module failed to declare one or more attributes. In this
        # case, silently continue to the next module.
