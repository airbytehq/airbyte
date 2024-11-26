#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object utilities** (i.e., supplementary low-level functions
handling arbitrary objects in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilObjectNameException
from beartype.typing import (
    Any,
    Optional,
)
from contextlib import AbstractContextManager

# ....................{ CLASSES                            }....................
class Iota(object):
    '''
    **Iota** (i.e., object minimizing space consumption by guaranteeably
    containing *no* attributes).
    '''

    __slots__ = ()

# ....................{ CONSTANTS                          }....................
SENTINEL = Iota()
'''
Sentinel object of arbitrary value.

This object is internally leveraged by various utility functions to identify
erroneous and edge-case input (e.g., iterables of insufficient length).
'''

# ....................{ TESTERS                            }....................
def is_object_context_manager(obj: object) -> bool:
    '''
    :data:`True` only if the passed object is a **context manager** (i.e.,
    object defining both the ``__exit__`` and ``__enter__`` dunder methods
    required to satisfy the context manager protocol).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this object is a context manager.
    '''

    # One-liners for frivolous inanity.
    return isinstance(obj, AbstractContextManager)


# Note that this tester function *CANNOT* be memoized by the @callable_cached
# decorator, which requires all passed parameters to already be hashable.
def is_object_hashable(obj: object) -> bool:
    '''
    :data:`True` only if the passed object is **hashable** (i.e., passable to
    the builtin :func:`hash` function *without* raising an exception and thus
    usable in hash-based containers like dictionaries and sets).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this object is hashable.
    '''

    # Attempt to hash this object. If doing so raises *any* exception
    # whatsoever, this object is by definition unhashable.
    #
    # Note that there also exists a "collections.abc.Hashable" superclass.
    # Sadly, this superclass is mostly useless for all practical purposes. Why?
    # Because user-defined classes are free to subclass that superclass
    # despite overriding the __hash__() dunder method implicitly called by the
    # builtin hash() function to raise exceptions: e.g.,
    #
    #     from collections.abc import Hashable
    #     class HashUmUp(Hashable):
    #         def __hash__(self):
    #             raise ValueError('uhoh')
    #
    # Note also that we catch all possible exceptions rather than merely the
    # standard "TypeError" exception raised by unhashable builtin types (e.g.,
    # dictionaries, lists, sets). Why? For the same exact reason as above.
    try:
        hash(obj)
    # If this object is unhashable, return false.
    except:
        return False

    # Else, this object is hashable. Return true.
    return True

# ....................{ GETTERS ~ name                     }....................
def get_object_name(obj: Any) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited string unambiguously
    identifying) of the passed object if this object defines either the
    ``__qualname__`` or ``__name__`` dunder attributes *or* raise an exception
    otherwise (i.e., if this object defines *no* such attributes).

    Specifically, this name comprises (in order):

    #. If this object is transitively declared by a module, the absolute name
       of that module.
    #. If this object is transitively declared by another object (e.g., class,
       callable) and thus nested in that object, the unqualified basenames of
       all parent objects transitively declaring this object in that module.
    #. Unqualified basename of this object.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Fully-qualified name of this object.

    Raises
    ----------
    _BeartypeUtilObjectNameException
        If this object defines neither ``__qualname__`` *nor* ``__name__``
        dunder attributes.
    '''

    # Avoid circular import dependencies.
    from beartype._cave._cavefast import CallableOrClassTypes
    from beartype._util.module.utilmodget import (
        get_object_module_name_or_none,
        get_object_type_module_name_or_none,
    )

    # Lexically scoped name of this object excluding this module name if this
    # object is named *OR* raise an exception otherwise.
    object_scopes_name = get_object_basename_scoped(obj)

    # Fully-qualified name of the module declaring this object if this object
    # is declared by a module *OR* "None" otherwise, specifically defined as:
    # * If this object is either a callable or class, the fully-qualified name
    #   of the module declaring this object.
    # * Else, the fully-qualified name of the module declaring the class of
    #   this object.
    object_module_name = (
        get_object_module_name_or_none(obj)
        if isinstance(object, CallableOrClassTypes) else
        get_object_type_module_name_or_none(obj)
    )

    # Return either...
    return (
        # If this module name exists, "."-delimited concatenation of this
        # module and object name;
        f'{object_module_name}.{object_scopes_name}'
        if object_module_name is not None else
        # Else, this object name as is.
        object_scopes_name
    )

# ....................{ GETTERS ~ basename                 }....................
def get_object_basename_scoped(obj: Any) -> str:
    '''
    **Lexically scoped name** (i.e., ``.``-delimited string unambiguously
    identifying all lexical scopes encapsulating) the passed object if this
    object defines either the ``__qualname__`` or ``__name__`` dunder
    attributes *or* raise an exception otherwise (i.e., if this object defines
    *no* such attributes).

    Specifically, this name comprises (in order):

    #. If this object is transitively declared by another object (e.g., class,
       callable) and thus nested in that object, the unqualified basenames of
       all parent objects transitively declaring this object in that module.
       For usability, these basenames intentionally omit the meaningless
       placeholder ``"<locals>"`` substrings artificially injected by Python
       itself into the original ``__qualname__`` instance variable underlying
       this getter: e.g.,

       .. code-block:: python

          >>> from beartype._util.utilobject import get_object_basename_scoped
          >>> def muh_func():
          ...     def muh_closure(): pass
          ...     return muh_closure()
          >>> muh_func().__qualname__
          'muh_func.<locals>.muh_closure'  # <-- bad Python
          >>> get_object_basename_scoped(muh_func)
          'muh_func.muh_closure'  # <-- good @beartype

    #. Unqualified basename of this object.

    Caveats
    ----------
    **The higher-level** :func:`get_object_name` **getter should typically be
    called instead of this lower-level getter.** This getter unsafely:

    * Requires the passed object to declare dunder attributes *not* generally
      declared by arbitrary instances of user-defined classes.
    * Omits the fully-qualified name of the module transitively declaring this
      object and thus fails to return fully-qualified names.

    **This high-level getter should always be called in lieu of directly
    accessing the low-level** ``__qualname__`` **dunder attribute on objects.**
    That attribute contains one meaningless ``"<locals>"`` placeholder
    substring conveying *no* meaningful semantics for each parent callable
    lexically nesting this object.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Lexically scoped name of this object.

    Raises
    ----------
    _BeartypeUtilObjectNameException
        If this object defines neither ``__qualname__`` *nor* ``__name__``
        dunder attributes.
    '''

    # Return the fully-qualified name of this object excluding its name,
    # constructed as follows:
    # * If this object defines the "__qualname__" dunder attribute whose value
    #   is the "."-delimited concatenation of the unqualified basenames of all
    #   parent objects transitively declaring this object, that value with all
    #   meaningless "<locals>" placeholder substrings removed. If this object
    #   is a nested non-method callable (i.e., pure-Python function nested in
    #   one or more parent pure-Python callables), that value contains one such
    #   placeholder for each parent callable containing this callable. Since
    #   placeholders convey no meaningful semantics, placeholders are removed.
    # * Else if this object defines the "__name__" dunder attribute whose value
    #   is the unqualified basename of this object, that value.
    # * Else, "None".
    object_scoped_name = getattr(
        obj, '__qualname__', getattr(
            obj, '__name__', None))

    # If this object is unnamed, raise a human-readable exception. The default
    # "AttributeError" exception raised by attempting to directly access either
    # the "obj.__name__" or "obj.__qualname__" attributes is sufficiently
    # non-explanatory to warrant replacement by our explanatory exception.
    if object_scoped_name is None:
        raise _BeartypeUtilObjectNameException(
            f'{repr(obj)} unnamed '
            f'(i.e., declares neither "__name__" nor "__qualname__" '
            f'dunder attributes).'
        )
    # Else, this object is named.

    # Remove all "<locals>" placeholder substrings as discussed above.
    return object_scoped_name.replace('<locals>.', '')

# ....................{ GETTERS ~ filename                 }....................
def get_object_filename_or_none(obj: object) -> Optional[str]:
    '''
    Filename of the module or script physically declaring the passed object if
    this object is either a callable or class physically declared on-disk *or*
    :data:`None` otherwise (i.e., if this object is neither a callable nor
    class *or* is either a callable or class dynamically declared in-memory).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    Optional[str]
        Either: 

        * If this object is either a callable or class physically declared
          on-disk, the filename of the module or script physically declaring
          this object.
        * Else, :data:`None`.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclsget import get_type_filename_or_none
    from beartype._util.func.utilfuncfile import get_func_filename_or_none
    from beartype._util.func.utilfunctest import is_func_python

    # Return either...
    return (
        # If this object is a pure-Python class, the absolute filename of the
        # source module file defining that class if that class was defined
        # on-disk *OR* "None" otherwise (i.e., if that class was defined
        # in-memory);
        get_type_filename_or_none(obj)
        if isinstance(obj, type) else
        # If this object is a pure-Python callable, the absolute filename of the
        # absolute filename of the source module file defining that callable if
        # that callable was defined on-disk *OR* "None" otherwise (i.e., if that
        # callable was defined in-memory);
        get_func_filename_or_none(obj)
        if is_func_python(obj) else
        # Else, "None".
        None
    )

# ....................{ GETTERS ~ type                     }....................
def get_object_type_unless_type(obj: object) -> type:
    '''
    Either the passed object if this object is a class *or* the class of this
    object otherwise (i.e., if this object is *not* a class).

    Note that this function *never* raises exceptions on arbitrary objects, as
    the :obj:`type` builtin wisely returns itself when passed itself: e.g.,

    .. code-block:: python

        >>> type(type(type)) is type
        True

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    type
        Type of this object.
    '''

    return obj if isinstance(obj, type) else type(obj)

# ....................{ GETTERS ~ type : name              }....................
def get_object_type_basename(obj: object) -> str:
    '''
    **Unqualified name** (i.e., non-``.``-delimited basename) of either the
    passed object if this object is a class *or* the class of this object
    otherwise (i.e., if this object is *not* a class).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Unqualified name of this class.
    '''

    # Elegant simplicity diminishes aggressive tendencies.
    return get_object_type_unless_type(obj).__name__


def get_object_type_name(obj: object) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring module) of either passed object if this object is a class *or*
    the class of this object otherwise (i.e., if this object is *not* a class).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Fully-qualified name of the type of this object.
    '''

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import (
        get_object_type_module_name_or_none)

    # Type of this object.
    cls = get_object_type_unless_type(obj)

    # Unqualified name of this type.
    cls_basename = get_object_type_basename(cls)

    # Fully-qualified name of the module defining this class if this class is
    # defined by a module *OR* "None" otherwise.
    cls_module_name = get_object_type_module_name_or_none(cls)

    # Return either...
    return (
        # The "."-delimited concatenation of this class basename and module
        # name if this module name exists.
        f'{cls_module_name}.{cls_basename}'
        if cls_module_name is not None else
        # This class basename as is otherwise.
        cls_basename
    )
