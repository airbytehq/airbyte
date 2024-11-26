#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype declarative type validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant
validators from arbitrary caller-defined classes tested via explicitly
supported object introspectors efficiently generating stack-free code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._is._valeisabc import _BeartypeValidatorFactoryABC
from beartype.vale._util._valeutilsnip import (
    VALE_CODE_CHECK_ISINSTANCE_TEST_format,
    VALE_CODE_CHECK_ISSUBCLASS_TEST_format,
)
from beartype.vale._core._valecore import BeartypeValidator
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TypeOrTupleTypes,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_type_isinstanceable,
    die_unless_type_or_types_isinstanceable,
    die_unless_type_issubclassable,
    die_unless_type_or_types_issubclassable,
)
from beartype._util.func.utilfuncscope import add_func_scope_attr
from beartype._util.utilobject import get_object_name

# ....................{ SUBCLASSES ~ instance              }....................
class _IsInstanceFactory(_BeartypeValidatorFactoryABC):
    '''
    **Beartype type instance validator factory** (i.e., object creating and
    returning a new beartype validator when subscripted (indexed) by any class,
    validating that :mod:`beartype`-decorated callable parameters and returns
    annotated by :attr:`typing.Annotated` type hints subscripted by that
    validator are objects whose classes subclass that class).

    This class efficiently validates that callable parameters and returns are
    instances of the arbitrary class subscripting (indexing) this factory. Any
    :mod:`beartype`-decorated callable parameter or return annotated by a
    :attr:`typing.Annotated` type hint subscripted by this factory subscripted
    by any class (e.g., ``typing.Annotated[type,
    beartype.vale.IsInstance[{cls}]]`` for any class ``{cls}``)
    validates that parameter or return value to be a subclass of that class.

    This factory generalizes :pep:`484`-compliant **isinstanceable types**
    (i.e., normal pure-Python and C-based classes that may be passed as the
    second parameter to the :func:`isinstance` builtin), because this factory
    does everything those types do and considerably more. Superficially,
    isinstanceable types also validate that callable parameters and returns are
    instances of those types. The similarity ends there, however.
    Isinstanceable types only narrowly apply to callable parameters and
    returns; meanwhile, this factory produces beartype validators universally
    applicable to both:

    * Callable parameters and returns.
    * **Attributes** of callable parameters and returns via the
      :class:`beartype.vale.IsAttr` factory.

    **This factory incurs no time performance penalties at call time.** Whereas
    the general-purpose :class:`beartype.vale.Is` factory necessarily calls
    the caller-defined callable subscripting that factory at call time and thus
    incurs a minor time performance penalty, this factory efficiently reduces
    to one-line tests in :mod:`beartype`-generated wrapper functions *without*
    calling any callables and thus incurs *no* time performance penalties.

    Examples
    ----------
    .. code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import IsInstance
       >>> from math import factorial as loose_factorial
       >>> from typing import Annotated

       # Type hint matching any non-boolean integer, generating code like:
       #    (isinstance(number, int) and not isinstance(number, bool)))
       # Surprisingly, booleans are literally integers in Python (e.g.,
       # ``issubclass(bool, int) is True``). Callable parameters and returns
       # annotated as accepting only integers thus implicitly accept booleans
       # as well by default. This type hint explicitly prevents that ambiguity.
       >>> IntNonbool = Annotated[int, ~IsInstance[bool]]

       # Annotate callables by those type hints.
       >>> @beartype
       ... def strict_factorial(integer: IntNonbool) -> IntNonbool:
       ...     """
       ...     Factorial of the passed integer, explicitly prohibiting booleans
       ...     masquerading as integers.
       ...     """
       ...     return loose_factorial(integer)

       # Call those callables with parameters satisfying those hints.
       >>> strict_factorial(42)
       1405006117752879898543142606244511569936384000000000

       # Call those callables with parameters violating those hints.
       >>> strict_factorial(True)
       beartype.roar.BeartypeCallHintParamViolation: @beartyped
       strict_factorial() parameter integer=True violates type hint
       typing.Annotated[int, ~IsInstance[builtins.bool]], as True violates
       validator ~IsInstance[builtins.bool]:

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further commentary.
    '''

    # ..................{ DUNDERS                            }..................
    @callable_cached
    def __getitem__(self, types: TypeOrTupleTypes) -> BeartypeValidator:  # type: ignore[override]
        '''
        Create and return a new beartype validator validating type instancing
        against at least one of the passed classes, suitable for subscripting
        :pep:`593`-compliant :attr:`typing.Annotated` type hints.

        This method is memoized for efficiency.

        Parameters
        ----------
        types : TypeOrTupleTypes
            One or more arbitrary classes to validate type instancing against.

        Returns
        ----------
        BeartypeValidator
            Beartype validator encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this factory was subscripted by either:

            * *No* arguments.
            * One or more arguments that are *not* **isinstanceable types**
              (i.e., classes passable as the second argument to the :func:
              `isinstance` builtin).

        See Also
        ----------
        :class:`_IsAttrFactory`
            Usage instructions.
        '''

        # Machine-readable string representing this type or tuple of types.
        types_repr = ''

        # If this factory was subscripted by either no arguments *OR* two or
        # more arguments...
        if isinstance(types, tuple):
            # If this factory was subscripted by *NO* arguments, raise an
            # exception.
            if not types:
                raise BeartypeValeSubscriptionException(
                    f'{self._getitem_exception_prefix}empty tuple.')
            # Else, this factory was subscripted by two or more arguments.

            # If any such argument is *NOT* an isinstanceable type, raise an
            # exception.
            die_unless_type_or_types_isinstanceable(
                type_or_types=types,
                exception_cls=BeartypeValeSubscriptionException,
                exception_prefix=self._getitem_exception_prefix,
            )
            # Else, all such arguments are isinstanceable types.

            # Append the fully-qualified name of each such type to this string.
            for cls in types:
                types_repr += f'{get_object_name(cls)}, '

            # Strip the suffixing ", " from this string for readability.
            types_repr = types_repr[:-2]
        # Else, this factory was subscripted by one argument. In this case...
        else:
            # If this argument is *NOT* an isinstanceable type, raise an
            # exception.
            die_unless_type_isinstanceable(
                cls=types,
                exception_cls=BeartypeValeSubscriptionException,
                exception_prefix=self._getitem_exception_prefix,
            )
            # Else, this argument is an isinstanceable type.

            # Fully-qualified name of this type.
            types_repr = get_object_name(types)

        # Callable inefficiently validating against this type.
        is_valid = lambda pith: isinstance(pith, types)

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: LexicalScope = {}

        # Name of a new parameter added to the signature of wrapper functions
        # whose value is this type or tuple of types, enabling this type or
        # tuple of types to be tested in those functions *WITHOUT* additional
        # stack frames.
        param_name_types = add_func_scope_attr(
            attr=types, func_scope=is_valid_code_locals)

        # Code snippet efficiently validating against this type.
        is_valid_code = VALE_CODE_CHECK_ISINSTANCE_TEST_format(
            param_name_types=param_name_types)

        # Create and return this subscription.
        return BeartypeValidator(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,

            # Intentionally pass this subscription's machine-readable
            # representation as a string rather than lambda function returning
            # a string, as this string is safely, immediately, and efficiently
            # constructable from these arguments' representation.
            get_repr=f'{self._basename}[{types_repr}]',
        )

# ....................{ SUBCLASSES ~ subclass              }....................
class _IsSubclassFactory(_BeartypeValidatorFactoryABC):
    '''
    **Beartype type inheritance validator factory** (i.e., object creating and
    returning a new beartype validator when subscripted (indexed) by any class,
    validating that :mod:`beartype`-decorated callable parameters and returns
    annotated by :attr:`typing.Annotated` type hints subscripted by that
    validator subclass that class).

    This class efficiently validates that callable parameters and returns are
    subclasses of the arbitrary class subscripting (indexing) this factory. Any
    :mod:`beartype`-decorated callable parameter or return annotated by a
    :attr:`typing.Annotated` type hint subscripted by this factory subscripted
    by any class (e.g., ``typing.Annotated[type,
    beartype.vale.IsSubclass[{cls}]]`` for any class ``{cls}``)
    validates that parameter or return value to be a subclass of that class.

    This factory generalizes the :pep:`484`-compliant :attr:`typing.Type` and :
    pep:`585`-compliant :class:`type` type hint factories, because this factory
    does everything those factories do and substantially more. Superficially, :
    attr:`typing.Type` and :class:`type` type hints also validate that callable
    parameters and returns are subclasses of the classes subscripting those
    hints. The similarity ends there, however. Those hints only narrowly apply
    to callable parameters and returns; meanwhile, this factory produces
    beartype validators universally applicable to both:

    * Callable parameters and returns.
    * **Attributes** of callable parameters and returns via the
      :class:`beartype.vale.IsAttr` factory.

    **This factory incurs no time performance penalties at call time.** Whereas
    the general-purpose :class:`beartype.vale.Is` factory necessarily calls
    the caller-defined callable subscripting that factory at call time and thus
    incurs a minor time performance penalty, this factory efficiently reduces
    to one-line tests in :mod:`beartype`-generated wrapper functions *without*
    calling any callables and thus incurs *no* time performance penalties.

    Examples
    ----------
    .. code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import IsAttr, IsSubclass
       >>> from typing import Annotated
       >>> import numpy as np

       # Type hint matching only NumPy arrays of floats of arbitrary precision,
       # generating code resembling:
       #    (isinstance(array, np.ndarray) and
       #     np.issubdtype(array.dtype, np.floating))
       >>> NumpyFloatArray = Annotated[
       ...     np.ndarray, IsAttr['dtype', IsAttr['type', IsSubclass[np.floating]]]]

       # Type hint matching only NumPy arrays of integers of arbitrary
       # precision, generating code resembling:
       #    (isinstance(array, np.ndarray) and
       #     np.issubdtype(array.dtype, np.integer))
       >>> NumpyIntArray = Annotated[
       ...     np.ndarray, IsAttr['dtype', IsAttr['type', IsSubclass[np.integer]]]]

       # NumPy arrays of well-known real number series.
       >>> E_APPROXIMATIONS = np.array(
       ...     [1+1, 1+1+1/2, 1+1+1/2+1/6, 1+1+1/2+1/6+1/24,])
       >>> FACTORIALS = np.array([1, 2, 6, 24, 120, 720, 5040, 40320, 362880,])

       # Annotate callables by those type hints.
       >>> @beartype
       ... def round_int(array: NumpyFloatArray) -> NumpyIntArray:
       ...     """
       ...     NumPy array of integers rounded from the passed NumPy array of
       ...     floating-point numbers to the nearest 64-bit integer.
       ...     """
       ...     return np.around(array).astype(np.int64)

       # Call those callables with parameters satisfying those hints.
       >>> round_int(E_APPROXIMATIONS)
       [2, 3, 3, 3]

       # Call those callables with parameters violating those hints.
       >>> round_int(FACTORIALS)
       beartype.roar.BeartypeCallHintParamViolation: @beartyped round_int()
       parameter array="array([ 1, 2, 6, 24, 120, 720, 5040, 40320, ...])"
       violates type hint typing.Annotated[numpy.ndarray, IsAttr['dtype',
       IsAttr['type', IsSubclass[numpy.floating]]]], as "array([ 1, 2, 6, 24,
       120, 720, 5040, 40320, ...])" violates validator IsAttr['dtype',
       IsAttr['type', IsSubclass[numpy.floating]]]

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further commentary.
    '''

    # ..................{ DUNDERS                            }..................
    @callable_cached
    def __getitem__(self, types: TypeOrTupleTypes) -> BeartypeValidator:  # type: ignore[override]
        '''
        Create and return a new beartype validator validating type inheritance
        against at least one of the passed classes, suitable for subscripting
        :pep:`593`-compliant :attr:`typing.Annotated` type hints.

        This method is memoized for efficiency.

        Parameters
        ----------
        types : TypeOrTupleTypes
            One or more arbitrary classes to validate type inheritance against.

        Returns
        ----------
        BeartypeValidator
            Beartype validator encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this factory was subscripted by either:

            * *No* arguments.
            * One or more arguments that are *not* **issubclassable types**
              (i.e., classes passable as the second argument to the :func:
              `issubclass` builtin).

        See Also
        ----------
        :class:`_IsAttrFactory`
            Usage instructions.
        '''

        # Machine-readable string representing this type or tuple of types.
        types_repr = ''

        # If this factory was subscripted by either no arguments *OR* two or
        # more arguments...
        if isinstance(types, tuple):
            # If this factory was subscripted by *NO* arguments, raise an
            # exception.
            if not types:
                raise BeartypeValeSubscriptionException(
                    f'{self._getitem_exception_prefix}empty tuple.')
            # Else, this factory was subscripted by two or more arguments.

            # If any such argument is *NOT* an issubclassable type, raise an
            # exception.
            die_unless_type_or_types_issubclassable(
                type_or_types=types,
                exception_cls=BeartypeValeSubscriptionException,
                exception_prefix=self._getitem_exception_prefix,
            )
            # Else, all such arguments are issubclassable types.

            # Append the fully-qualified name of each such type to this string.
            for cls in types:
                types_repr += f'{get_object_name(cls)}, '

            # Strip the suffixing ", " from this string for readability.
            types_repr = types_repr[:-2]
        # Else, this factory was subscripted by one argument. In this case...
        else:
            # If this argument is *NOT* an issubclassable type, raise an
            # exception.
            die_unless_type_issubclassable(
                cls=types,
                exception_cls=BeartypeValeSubscriptionException,
                exception_prefix=self._getitem_exception_prefix,
            )
            # Else, this argument is an issubclassable type.

            # Fully-qualified name of this type.
            types_repr = get_object_name(types)

        # Callable inefficiently validating against this type.
        is_valid = lambda pith: is_type_subclass(pith, types)

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: LexicalScope = {}

        # Name of a new parameter added to the signature of wrapper functions
        # whose value is this type or tuple of types, enabling this type or
        # tuple of types to be tested in those functions *WITHOUT* additional
        # stack frames.
        param_name_types = add_func_scope_attr(
            attr=types, func_scope=is_valid_code_locals)

        # Code snippet efficiently validating against this type.
        is_valid_code = VALE_CODE_CHECK_ISSUBCLASS_TEST_format(
            param_name_types=param_name_types)

        # Create and return this subscription.
        return BeartypeValidator(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,

            # Intentionally pass this subscription's machine-readable
            # representation as a string rather than lambda function returning
            # a string, as this string is safely, immediately, and efficiently
            # constructable from these arguments' representation.
            get_repr=f'{self._basename}[{types_repr}]',
        )
