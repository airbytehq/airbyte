#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint factories** (i.e., low-level classes and callables
dynamically creating and returning PEP-compliant type hints, typically as a
runtime fallback when the currently installed versions of the standard
:mod:`typing` module and third-party :mod:`typing_extensions` modules do *not*
officially support those factories).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Generic,
    Type,
    TypeVar,
)
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ PRIVATE ~ hints                    }....................
_T = TypeVar('_T')
'''
PEP-compliant type variable matching any arbitrary object.
'''

# ....................{ METACLASSES                        }....................
class _TypeHintTypeFactoryMeta(type):
    '''
    **Type hint type factory metaclass** (i.e., the root :class:`type` metaclass
    augmented with caching to memoize singleton instances of the
    :class:`TypeHintTypeFactory` class declared below).

    This metaclass is superior to the usual approach of implementing the
    singleton design pattern: overriding the :meth:`__new__` method of a
    singleton class to conditionally create a new instance of that class only if
    an instance has *not* already been created. Why? Because that approach
    unavoidably re-calls the :meth:`__init__` method of a previously initialized
    singleton instance on each instantiation of that class. Doing so is
    generally considered harmful.

    This metaclass instead guarantees that the :meth:`__init__` method of a
    singleton instance is only called exactly once on the first instantiation of
    that class.
    '''

    # ..................{ INITIALIZERS                       }..................
    @callable_cached
    def __call__(cls, type_factory: type) -> 'TypeHintTypeFactory':  # type: ignore[override]
        '''
        Instantiate the passed singleton class with the passed arbitrary type.

        Parameters
        ----------
        cls : Type['TypeHintTypeFactory']
            :class:`TypeHintTypeFactory` class to be instantiated.
        type_factory : type
            Arbitrary type to instantiate that class with.
        '''

        # Create and return a new memoized singleton instance of the
        # "TypeHintTypeFactory" class specific to this arbitrary type.
        return super().__call__(type_factory)

# ....................{ CLASSES                            }....................
class TypeHintTypeFactory(Generic[_T], metaclass=_TypeHintTypeFactoryMeta):
    '''
    **Type hint type factory** (i.e., high-level object unconditionally
    returning an arbitrary type when subscripted by any arbitrary object).

    This factory is principally intended to serve as a graceful runtime fallback
    when the currently installed versions of the standard :mod:`typing` module
    and third-party :mod:`typing_extensions` modules do *not* declare the
    desired PEP-compliant type hint factory. See the examples below.

    Instances of this class are implicitly memoized as singletons as a
    negligible space and time optimization that costs us nothing and gains us a
    negligible something.

    Examples
    ----------
    For example, the :pep:`647`-compliant :attr:`typing.TypeGuard` type hint
    factory is only available from :mod:`typing` under  Python >= 3.10 or from
    :mod:`typing_extensions` if optionally installed; if neither of those two
    conditions apply, this factory may be trivially used as a fake ``TypeGuard``
    stand-in returning the builtin :class:`bool` type when subscripted --
    exactly as advised by :pep:`647` itself: e.g.,

    .. code-block:

       from beartype.typing import TYPE_CHECKING
       from beartype._util.hint.utilhintfactory import TypeHintTypeFactory
       from beartype._util.module.lib.utiltyping import (
           import_typing_attr_or_fallback)

       if TYPE_CHECKING:
           from typing_extensions import TypeGuard
       else:
           TypeGuard = import_typing_attr_or_fallback(
               'TypeGuard', TypeHintTypeFactory(bool))

       # This signature gracefully reduces to the following at runtime under
       # Python <= 3.10 if "typing_extensions" is *NOT* installed:
       #     def is_obj_list(obj: object) -> bool:
       def is_obj_list(obj: object) -> TypeGuard[list]:
           return isinstance(obj, list)

    Attributes
    ----------
    _type_factory : Type[_T]
        Arbitrary type to be returned from the :meth:`__getitem__` method.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_type_factory',
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, type_factory: Type[_T]) -> None:
        '''
        Initialize this type hint type factory.

        Parameters
        ----------
        type_factory : Type[_T]
            Arbitrary type to be returned from the :meth:`__getitem__` method.
        '''
        assert isinstance(type_factory, type), f'{repr(type_factory)} not type.'

        # Classify all passed parameters.
        self._type_factory = type_factory

    # ..................{ DUNDERS                            }..................
    def __getitem__(self, index: object) -> Type[_T]:
        '''
        Return the arbitrary type against which this type hint type factory was
        originally initialized when subscripted by the passed arbitrary object.

        Parameters
        ----------
        index : object
            Arbitrary object. Although this is typically a PEP-compliant type
            hint, this factory imposes *no* constraints on this object.

        Parameters
        ----------
        Type[_T]
            Arbitrary type previously passed to the :meth:`__init__` method.
        '''

        # Return this type, silently ignoring the passed object entirely. Hah!
        return self._type_factory
