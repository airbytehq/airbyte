#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype declarative operator validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant
validators from arbitrary caller-defined objects tested via explicitly
supported operators efficiently generating stack-free code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: *Useful optimization.* For "_IsEqualFactory", we can (and should)
#directly embed the values of builtins when comparing against builtins (e.g.,
#integers, strings). Specifically, we should only conditionally perform this
#line below:
#       param_name_obj_value = add_func_scope_attr(
#           attr=obj, func_scope=is_valid_code_locals)
#...when we absolutely must. So when mustn't we? We see two simple approaches
#to detecting builtin objects:
#* Detect the types of those objects. While obvious, this presents several
#  subtleties:
#  * Fake builtin objects, which would naturally need to be excluded.
#  * Subclasses of builtin objects, which would *ALSO* need to be excluded.
#  In short, "isinstance(param_name_obj_value, TUPLE_OF_TRUE_BUILTIN_TYPES)"
#  fails to suffice -- although something more brute-force like
#  "type(param_name_obj_value) in SET_OF_TRUE_BUILTIN_TYPES" might suffice.
#* Detect the first character of their repr() strings as belonging to the set:
#      BUILTIN_OBJ_REPR_CHARS_FIRST = {
#          "'", '"', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
#      repr(param_name_obj_value) in BUILTIN_OBJ_REPR_CHARS_FIRST
#We like the latter quite a bit more, as it has *NO* obvious edge cases,
#requires *NO* hard-coding of types, and appears to scale gracefully. The only
#downside is that it assumes third-party repr() strings to be sane, but... if
#that *ISN'T* the case, that is a bug in those third-parties. *shrug*

#FIXME: Generalize to support arbitrary binary operators by:
#* Define a new "_IsOperatorBinaryABC(_BeartypeValidatorFactoryABC, metaclass=ABCMeta)" superclass.
#* In that superclass:
#  * Define a stock __class_getitem__() method whose implementation is
#    sufficiently generic so as to be applicable to all subclasses. To do so,
#    this method should access class variables defined by those subclasses.
#  * Note that there is absolutely no reason or point to define abstract class
#    methods forcing subclasses to define various metadata, for the unfortunate
#    reason that abstract class methods do *NOT* actually enforce subclasses
#    that aren't instantiable anyway to implement those methods. *sigh*
#* Refactor "_IsEqualFactory" to:
#  * Subclass that superclass.
#  * Define the following class variables, which the superclass
#    __class_getitem__() method will internally access to implement itself:
#    from operator import __eq__
#
#    class _IsEqualFactory(_IsOperatorBinaryABC):
#        _operator = __eq__
#        _operator_code = '=='
#
#Ridiculously sweet, eh? We know.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.typing import Any
from beartype.vale._is._valeisabc import _BeartypeValidatorFactoryABC
from beartype.vale._util._valeutilsnip import (
    VALE_CODE_CHECK_ISEQUAL_TEST_format)
from beartype.vale._core._valecore import BeartypeValidator
from beartype._data.hint.datahinttyping import LexicalScope
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.utilfuncscope import add_func_scope_attr

# ....................{ SUBCLASSES ~ equal                 }....................
class _IsEqualFactory(_BeartypeValidatorFactoryABC):
    '''
    **Beartype object equality validator factory** (i.e., object creating and
    returning a new beartype validator when subscripted (indexed) by any
    object, validating that :mod:`beartype`-decorated callable parameters and
    returns annotated by :attr:`typing.Annotated` type hints subscripted by
    that validator equal that object).

    This class efficiently validates that callable parameters and returns are
    equal to the arbitrary object subscripting this factory. Any
    :mod:`beartype`-decorated callable parameter or return annotated by a
    :attr:`typing.Annotated` type hint subscripted by this factory subscripted
    by any object (e.g., ``typing.Annotated[{cls},
    beartype.vale.IsEqual[{obj}]]`` for any class ``{cls}``  and object
    ``{obj}`) validates that parameter or return value to equal that object
    under the standard ``==`` equality comparison.

    This factory is a generalization of the :pep:`586`-compliant
    :attr:`typing.Literal` type hint factory, because this factory does
    everything that factory does and substantially more. Superficially,
    :attr:`typing.Literal` type hints also validate that callable parameters
    and returns are equal to (i.e., ``==``) the literal object subscripting
    those hints. The similarity ends there, however. :attr:`typing.Literal` is
    only subscriptable by literal :class:`bool`, :class:`bytes`, :class:`int`,
    :class:`str`, :class:`Enum`, and ``type(None)`` objects; meanwhile, this
    factory is subscriptable by *any* object.

    **This factory incurs no time performance penalties at call time.** Whereas
    the general-purpose :class:`beartype.vale.Is` factory necessarily calls
    the caller-defined callable subscripting that factory at call time and thus
    incurs a minor time performance penalty, this factory efficiently reduces
    to one-line tests in :mod:`beartype`-generated wrapper functions *without*
    calling any callables and thus incurs *no* time performance penalties.

    Caveats
    ----------
    **This class is intentionally subscriptable by only a single object.** Why?
    Disambiguity. When subscripted by variadic positional (i.e., one or more)
    objects, this class internally treats those objects as items of a tuple to
    validate equality against rather than as independent objects to iteratively
    validate equality against. Since this is non-intuitive, callers should avoid
    subscripting this class by multiple objects. Although non-intuitive, this is
    also unavoidable. The ``__class_getitem__()`` dunder method obeys the same
    semantics as the ``__getitem__()`` dunder method, which is unable to
    differentiate between being subscripted two or more objects and being
    subscripted by a tuple of two or more objects. Since being able to validate
    equality against tuples of two or more objects is essential and since this
    class being subscripted by two or more objects would trivially reduce to
    shorthand for the existing ``|`` set operator already supported by this
    class, this class preserves support for tuples of two or more objects at a
    cost of non-intuitive results when subscripted by multiple objects.

    Don't blame us. We didn't vote for :pep:`560`.

    Examples
    ----------
    .. code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import IsEqual
       >>> from typing import Annotated

       # Lists of the first ten items of well-known simple whole number series.
       >>> WHOLE_NUMBERS      = [0, 1, 2, 3, 4,  5,  6,  7,  8,  9]
       >>> WHOLE_NUMBERS_EVEN = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
       >>> WHOLE_NUMBERS_ODD  = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

       # Type hint matching only lists of integers equal to one of these lists.
       >>> SimpleWholeNumberSeries = Annotated[
       ...     list[int],
       ...     IsEqual[WHOLE_NUMBERS] |
       ...     IsEqual[WHOLE_NUMBERS_EVEN] |
       ...     IsEqual[WHOLE_NUMBERS_ODD]
       ... ]

       # Annotate callables by those type hints.
       >>> @beartype
       ... def guess_next(series: SimpleWholeNumberSeries) -> int:
       ...     """
       ...     Guess the next whole number in the passed whole number series.
       ...     """
       ...     if series == WHOLE_NUMBERS: return WHOLE_NUMBERS[-1] + 1
       ...     else:                       return        series[-1] + 2

       # Call those callables with parameters equal to one of those objects.
       >>> guess_next(list(range(10)))
       10
       >>> guess_next([number*2 for number in range(10)])
       20

       # Call those callables with parameters unequal to one of those objects.
       >>> guess_next([1, 2, 3, 6, 7, 14, 21, 42,])
       beartype.roar.BeartypeCallHintParamViolation: @beartyped guess_next()
       parameter series=[1, 2, 3, 6, 7, 14, 21, 42] violates type hint
       typing.Annotated[list[int], IsEqual[[0, 1, 2, 3, 4, 5, 6, 7, 8,
       9]] | IsEqual[[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]] | IsEqual[[1, 3, 5,
       7, 9, 11, 13, 15, 17, 19]]], as value [1, 2, 3, 6, 7, 14, 21, 42]
       violates validator IsEqual[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]] |
       IsEqual[[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]] | IsEqual[[1, 3, 5, 7, 9,
       11, 13, 15, 17, 19]].

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further commentary.
    '''

    # ..................{ DUNDERS                            }..................
    @callable_cached
    def __getitem__(self, obj: Any) -> BeartypeValidator:  # type: ignore[override]
        '''
        Create and return a new beartype validator validating equality against
        the passed object, suitable for subscripting :pep:`593`-compliant
        :attr:`typing.Annotated` type hints.

        This method is memoized for efficiency.

        Parameters
        ----------
        obj : Any
            Arbitrary object to validate equality against.

        Returns
        ----------
        BeartypeValidator
            Beartype validator encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this factory was subscripted by either:

            * *No* arguments.
            * Two or more arguments.

        See Also
        ----------
        :class:`_IsEqualFactory`
            Usage instructions.
        '''

        # If...
        if (
            # This factory was subscripted by either no arguments *OR* two or
            # more arguments *AND*...
            isinstance(obj, tuple) and
            # This factory was subscripted by no arguments...
            not obj
        # Then raise an exception.
        ):
            raise BeartypeValeSubscriptionException(
                f'{self._getitem_exception_prefix}empty tuple.')
        # Else, this factory was subscripted by one or more arguments. In any
        # case, accept this object as is. See the class docstring for details.
        # print(f'_IsEqualFactory[{repr(obj)}]')

        # Callable inefficiently validating against this object.
        is_valid = lambda pith: pith == obj

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: LexicalScope = {}

        # Name of a new parameter added to the signature of wrapper functions
        # whose value is this object, enabling this object to be tested in
        # those functions *WITHOUT* additional stack frames.
        param_name_obj_value = add_func_scope_attr(
            attr=obj, func_scope=is_valid_code_locals)

        # Code snippet efficiently validating against this object.
        is_valid_code = VALE_CODE_CHECK_ISEQUAL_TEST_format(
            param_name_obj_value=param_name_obj_value)

        # Create and return this subscription.
        return BeartypeValidator(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,
            get_repr=lambda: f'{self._basename}[{repr(obj)}]',
        )
