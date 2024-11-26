#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validation superclasses** (i.e., :mod:`beartype`-specific abstract
base classes (ABCs) from all concrete beartype validation subclasses derive).

This private submodule defines the core low-level class hierarchy driving the
entire :mod:`beartype` data validation ecosystem.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta, abstractmethod
from beartype.roar import BeartypeValeSubscriptionException
from beartype.typing import Any
from beartype.vale._core._valecore import BeartypeValidator
from beartype._util.text.utiltextrepr import represent_object

# ....................{ METACLASSES                        }....................
class _BeartypeValidatorFactoryABCMeta(ABCMeta):
    '''
    Metaclass all **beartype validator factory subclasses** (i.e.,
    :class:`_BeartypeValidatorFactoryABC` subclasses).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(cls, classname, superclasses, attr_name_to_value) -> None:
        super().__init__(classname, superclasses, attr_name_to_value)

        # Sanitize the fully-qualified name of the module declaring this class
        # from the private name of the module implementing this classes to the
        # public name of the module exporting this class, improving end user
        # clarity and usability.
        cls.__module__ = 'beartype.vale'

# ....................{ SUPERCLASSES                       }....................
#FIXME: Pyright appears to be extremely confused. It thinks that the
#"_BeartypeValidatorFactoryABCMeta" metaclass is a "generic" (i.e., subclasses
#"typing.Generic"), when in fact that metaclass merely subclasses the standard
#"abc.ABCMeta" metaclass. Consider submitting an upstream pyright issue, please.
class _BeartypeValidatorFactoryABC(
    object, metaclass=_BeartypeValidatorFactoryABCMeta):  # pyright: ignore[reportGeneralTypeIssues]
    '''
    Abstract base class of all **beartype validator factory subclasses**
    (i.e., subclasses that, when subscripted (indexed) by subclass-specific
    objects, create new :class:`BeartypeValidator` objects encapsulating those
    objects, themselves suitable for subscripting (indexing)
    :attr:`typing.Annotated` type hints, themselves enforcing subclass-specific
    validation constraints and contracts on :mod:`beartype`-decorated callable
    parameters and returns annotated by those hints).

    Attributes
    ----------
    _basename : str
        Machine-readable basename of the public factory singleton
        instantiating this private factory subclass (e.g., ``"IsAttr"``).
    _getitem_exception_prefix : str
        Human-readable substring prefixing exceptions raised by the subclass
        implementation of the abstract :meth:__getitem__` dunder method.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, basename: str) -> None:
        '''
        Initialize this subclass instance.

        Parameters
        ----------
        basename : str
            Machine-readable basename of the public factory singleton
            instantiating this private factory subclass (e.g., ``"IsAttr"``).
        '''
        assert isinstance(basename, str), f'{repr(basename)} not string.'

        # Classify all passed parameters.
        self._basename = basename

        # Initialize all remaining instance variables.
        self._getitem_exception_prefix = (
            f'Beartype validator factory "{self._basename}" '
            f'subscripted by '
        )

    # ..................{ ABSTRACT ~ dunder                  }..................
    @abstractmethod
    def __getitem__(self, *args, **kwargs) -> BeartypeValidator:
        '''
        Create and return a new beartype validator validating the subclass
        constraint parametrized by the passed arguments subscripting this
        beartype validator factory.

        Like standard type hints (e.g., :attr:`typing.Union`), instances of
        concrete subclasses of this abstract base class (ABC) are *only*
        intended to be subscripted (indexed).

        Concrete subclasses are required to implement this abstract method.
        Concrete subclasses are strongly recommended (but *not* required) to
        memoize their implementations by the
        :func:`beartype._util.cache.utilcachecall.callable_cached` decorator.

        Returns
        ----------
        BeartypeValidator
            Beartype validator encapsulating this validation.
        '''

        pass

    # ..................{ PRIVATE ~ validator                }..................
    #FIXME: Unit test us up, please.
    def _die_unless_getitem_args_1(self, args: Any) -> None:
        '''
        Raise an exception unless this beartype validator factory was
        subscripted (indexed) by exactly one argument.

        This validator is intended to be called by concrete subclass
        implementations of the :meth:`__getitem__` dunder method to validate
        the arguments subscripting this beartype validator factory.

        Parameters
        ----------
        args : Any
            Variadic positional arguments to be inspected.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If the caller dunder method was passed either:

            * No arguments.
            * Two or more arguments.
        '''

        # If this object was subscripted by either no arguments or two or more
        # arguments, raise an exception. Specifically...
        if isinstance(args, tuple):
            # If this object was subscripted by two or more arguments, raise a
            # human-readable exception.
            if args:
                raise BeartypeValeSubscriptionException(
                    f'{self._getitem_exception_prefix}two or more arguments '
                    f'{represent_object(args)}.'
                )
            # Else, this object was subscripted by *NO* arguments. In this case,
            # raise a human-readable exception.
            else:
                raise BeartypeValeSubscriptionException(
                    f'{self._getitem_exception_prefix}empty tuple.')
        # Else, this object was subscripted by exactly one argument.
