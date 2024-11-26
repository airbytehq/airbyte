#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **declarative object validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant
validators from arbitrary caller-defined objects tested via explicitly
supported object introspectors efficiently generating stack-free code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.typing import Any, Tuple
from beartype.vale._is._valeisabc import _BeartypeValidatorFactoryABC
from beartype.vale._util._valeutilsnip import (
    VALE_CODE_CHECK_ISATTR_TEST_format,
    VALE_CODE_CHECK_ISATTR_VALUE_EXPR_format,
    VALE_CODE_INDENT_1,
)
from beartype.vale._core._valecore import BeartypeValidator
from beartype._data.hint.datahinttyping import LexicalScope
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.kind.utilkinddict import update_mapping
from beartype._util.func.utilfuncscope import add_func_scope_attr
from beartype._util.text.utiltextrepr import represent_object
from beartype._util.utilobject import SENTINEL

# ....................{ SUBCLASSES ~ attr                  }....................
class _IsAttrFactory(_BeartypeValidatorFactoryABC):
    '''
    **Beartype object attribute validator factory** (i.e., object creating and
    returning a new beartype validator when subscripted (indexed) by both the
    name of any object attribute *and* any **attribute validator** (i.e., other
    beartype validator created by subscripting any :mod:`beartype.vale` class),
    validating that :mod:`beartype`-decorated callable parameters and returns
    annotated by :attr:`typing.Annotated` type hints subscripted by the former
    validator define an attribute with that name satisfying that attribute
    validator).

    This class efficiently validates that callable parameters and returns
    define arbitrary object attributes satisfying arbitrary validators
    subscripting this factory. Any :mod:`beartype`-decorated callable parameter
    or return annotated by a :attr:`typing.Annotated` type hint subscripted by
    this factory subscripted by any object attribute name and validator (e.g.,
    ``typing.Annotated[{cls}, beartype.vale.IsAttr[{attr_name},
    {attr_validator}]]`` for any class ``{cls}``, object attribute name
    ``{attr_name}`, and object attribute validator ``{attr_validator}``)
    validates that parameter or return value to be an instance of that class
    defining an attribute with that name satisfying that attribute validator.

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
       >>> from beartype.vale import IsAttr, IsEqual
       >>> from typing import Annotated
       >>> import numpy as np

       # Type hint matching only two-dimensional NumPy arrays of 64-bit floats,
       # generating code resembling:
       #    (isinstance(array, np.ndarray) and
       #     array.ndim == 2 and
       #     array.dtype == np.dtype(np.float64))
       >>> Numpy2dFloat64Array = Annotated[
       ...     np.ndarray,
       ...     IsAttr['ndim', IsEqual[2]],
       ...     IsAttr['dtype', IsEqual[np.dtype(np.float64)]],
       ... ]

       # Type hint matching only one-dimensional NumPy arrays of 64-bit floats,
       # generating code resembling:
       #    (isinstance(array, np.ndarray) and
       #     array.ndim == 2 and
       #     array.dtype.type == np.float64)
       >>> Numpy1dFloat64Array = Annotated[
       ...     np.ndarray,
       ...     IsAttr['ndim', IsEqual[2]],
       ...     # Nested attribute validators test equality against a "."-delimited
       ...     # attribute lookup (e.g., "dtype.type"), as expected.
       ...     IsAttr['dtype', IsAttr['type', IsEqual[np.float64]]],
       ... ]

       # NumPy arrays of well-known real number series.
       >>> FAREY_2D_FLOAT64_ARRAY = np.array(
       ...     [[0/1, 1/8,], [1/7, 1/6,], [1/5, 1/4], [2/7, 1/3], [3/8, 2/5]])
       >>> FAREY_1D_FLOAT64_ARRAY = np.array(
       ...     [3/7, 1/2, 4/7, 3/5, 5/8, 2/3, 5/7, 3/4, 4/5, 5/6, 6/7, 7/8])

       # Annotate callables by those type hints.
       >>> @beartype
       ... def sqrt_sum_2d(
       ...     array: Numpy2dFloat64Array) -> Numpy1dFloat64Array:
       ...     """
       ...     One-dimensional NumPy array of 64-bit floats produced by first
       ...     summing the passed two-dimensional NumPy array of 64-bit floats
       ...     along its second dimension and then square-rooting those sums.
       ...     """
       ...     return np.sqrt(array.sum(axis=1))

       # Call those callables with parameters satisfying those hints.
       >>> sqrt_sum_2d(FAREY_2D_FLOAT64_ARRAY)
       [0.35355339 0.55634864 0.67082039 0.78679579 0.88034084]

       # Call those callables with parameters violating those hints.
       >>> sqrt_sum_2d(FAREY_1D_FLOAT64_ARRAY)
       beartype.roar.BeartypeCallHintParamViolation: @beartyped
       sqrt_sum_2d() parameter array="array([0.42857143, 0.5, 0.57142857, 0.6,
       0.625, ...])" violates type hint typing.Annotated[numpy.ndarray,
       IsAttr['ndim', IsEqual[2]], IsAttr['dtype', IsEqual[dtype('float64')]]],
       as value "array([0.42857143, 0.5, 0.57142857, 0.6, 0.625, ...])"
       violates validator IsAttr['ndim', IsEqual[2]].

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further commentary.
    '''

    # ..................{ DUNDERS                            }..................
    @callable_cached
    def __getitem__(  # type: ignore[override]
        self, args: Tuple[str, BeartypeValidator]) -> BeartypeValidator:
        '''
        Create and return a new beartype validator validating object attributes
        with the passed name satisfying the passed validator, suitable for
        subscripting :pep:`593`-compliant :attr:`typing.Annotated` type hints.

        This method is memoized for efficiency.

        Parameters
        ----------
        args : Tuple[str, BeartypeValidator]
            2-tuple ``(attr_name, attr_validator)``, where:

            * ``attr_name`` is the arbitrary attribute name to validate that
              parameters and returns define satisfying the passed validator.
            * ``attr_validator`` is the attribute validator to validate that
              attributes with the passed name of parameters and returns
              satisfy.

        Returns
        ----------
        BeartypeValidator
            Beartype validator encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this factory was subscripted by either:

            * *No* arguments.
            * One argument.
            * Three or more arguments.

        See Also
        ----------
        :class:`_IsAttrFactory`
            Usage instructions.
        '''

        # If this class was subscripted by one non-tuple argument, raise an
        # exception.
        if not isinstance(args, tuple):
            raise BeartypeValeSubscriptionException(
                f'{self._getitem_exception_prefix}non-tuple argument '
                f'{represent_object(args)}.'
            )
        # Else, this class was subscripted by either no *OR* two or more
        # arguments (contained in this tuple).
        #
        # If this class was *NOT* subscripted by two arguments...
        elif len(args) != 2:
            # If this class was subscripted by one or more arguments, then by
            # deduction this class was subscripted by three or more arguments.
            # In this case, raise a human-readable exception.
            if args:
                raise BeartypeValeSubscriptionException(
                    f'{self._getitem_exception_prefix}three or more arguments '
                    f'{represent_object(args)}.'
                )
            # Else, this class was subscripted by *NO* arguments. In this case,
            # raise a human-readable exception.
            else:
                raise BeartypeValeSubscriptionException(
                    f'{self._getitem_exception_prefix}empty tuple.')
        # Else, this class was subscripted by exactly two arguments.

        # Localize these arguments to human-readable local variables.
        attr_name, attr_validator = args

        # Representer (i.e., callable accepting *NO* arguments returning a
        # machine-readable representation of this validator), defined *AFTER*
        # localizing these validator arguments.
        get_repr = lambda: (
            f'{self._basename}[{repr(attr_name)}, {repr(attr_validator)}]')

        # If this name is *NOT* a string, raise an exception.
        if not isinstance(attr_name, str):
            raise BeartypeValeSubscriptionException(
                f'{get_repr()} first argument '
                f'{represent_object(attr_name)} not string.'
            )
        # Else, this name is a string.
        #
        # If this name is the empty string, raise an exception.
        elif not attr_name:
            raise BeartypeValeSubscriptionException(
                f'{get_repr()} first argument is empty string.')
        # Else, this name is a non-empty string.
        #
        # Note that this name has *NOT* yet been validated to be valid Python
        # identifier. While we could do so here by calling our existing
        # is_identifier() tester, doing so would inefficiently repeat
        # the split on "." characters performed below. Instead, we iteratively
        # validate each split substring to be a valid Python identifier below.

        # Callable inefficiently validating object attributes with this name
        # against this validator.
        # is_valid: BeartypeValidatorTester = None  # type: ignore[assignment]

        # Code snippet efficiently validating object attributes with this name
        # against this validator.
        is_valid_code = ''

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: LexicalScope = {}

        # If this attribute name is unqualified (i.e., contains no "."
        # delimiters), prefer an efficient optimization avoiding iteration.
        if '.' not in attr_name:
            # If this name is *NOT* a valid Python identifier, raise an
            # exception.
            if not attr_name.isidentifier():
                raise BeartypeValeSubscriptionException(
                    f'{get_repr()} first argument {repr(attr_name)} not '
                    f'syntactically valid Python identifier.'
                )
            # Else, this name is a valid Python identifier.

            def is_valid(pith: Any) -> bool:
                f'''
                ``True`` only if the passed object defines an attribute named
                "{attr_name}" whose value satisfies the validator
                {repr(attr_validator)}.
                '''

                # Attribute of this object with this name if this object
                # defines such an attribute *OR* a sentinel placeholder
                # otherwise (i.e., if this object defines *NO* such attribute).
                pith_attr = getattr(pith, attr_name, SENTINEL)

                # Return true only if...
                return (
                    # This object defines an attribute with this name *AND*...
                    pith_attr is not SENTINEL and
                    # This attribute satisfies this validator.
                    attr_validator.is_valid(pith_attr)
                )

            # Names of new parameters added to the signature of wrapper
            # functions enabling this validator to be tested in those functions
            # *WITHOUT* additional stack frames whose values are:
            # * The sentinel placeholder.
            #
            # Add these parameters *BEFORE* generating locals.
            local_name_sentinel = add_func_scope_attr(
                attr=SENTINEL, func_scope=is_valid_code_locals)

            # Generate locals safely merging the locals required by both the
            # code generated below *AND* the externally provided code
            # validating this attribute.
            update_mapping(
                mapping_trg=is_valid_code_locals,
                mapping_src=attr_validator._is_valid_code_locals,
            )

            #FIXME: Unfortunately, "local_name_attr_value" still isn't a
            #sufficiently unique name below, because "IsAttr['name',
            #IsAttr['name', IsEqual[True]]]" is a trivial counter-example where
            #the current approach breaks down. For true uniquification here,
            #we're going to need to instead:
            #* Define a global private counter:
            #  _local_name_obj_attr_value_counter = Counter(0)
            #* Replace the assignment below with:
            #  local_name_obj_attr_value = (
            #      f'{{obj}}_isattr_'
            #      f'{next(_local_name_obj_attr_value_counter)}'
            #  )
            #Of course, this assumes "Counter" objects are thread-safe. If
            #they're not, we'll need to further obfuscate all this behind a
            #[R]Lock of some sort. *sigh*
            #FIXME: Oh, right. We mixed up "collections.Counter" with
            #"itertools.count". The former is orthogonal to our interests here;
            #the latter is of interest but *NOT* thread-safe. The solution is
            #for us to implement a new "FastWriteCounter" class resembling that
            #published in this extremely clever (and thus awesome) article:
            #    https://julien.danjou.info/atomic-lock-free-counters-in-python

            # Name of a local variable in this code whose:
            # * Name is sufficiently obfuscated as to be hopefully unique to
            #   the code generated by this validator.
            # * Value is the value of this attribute of the arbitrary object
            #   being validated by this code.
            local_name_attr_value = f'{{obj}}_isattr_{attr_name}'

            # Python expression expanding to the value of this attribute,
            # efficiently optimized under Python >= 3.8 with an assignment
            # expression to avoid inefficient access of this value.
            attr_value_expr = VALE_CODE_CHECK_ISATTR_VALUE_EXPR_format(
                attr_name_expr=repr(attr_name),
                local_name_attr_value=local_name_attr_value,
                local_name_sentinel=local_name_sentinel,
            )

            # Python expression validating the value of this attribute,
            # formatted so as to be safely embeddable in the larger code
            # expression defined below.
            attr_value_is_valid_expr = (
                attr_validator._is_valid_code.format(
                    # Replace the placeholder substring "{obj}" in this code
                    # with the expression expanding to this attribute's value,
                    # defined as the name of the local variable previously
                    # assigned the value of this attribute by the
                    # "VALE_CODE_CHECK_ISATTR_VALUE_EXPR" code snippet
                    # subsequently embedded in the
                    # "VALE_CODE_CHECK_ISATTR_VALUE_TEST" code snippet.
                    obj=local_name_attr_value,
                    # Replace the placeholder substring "{indent}" in this code
                    # with an indentation increased by one level.
                    indent=VALE_CODE_INDENT_1,
                ))

            # Code snippet efficiently validating against this object.
            is_valid_code = VALE_CODE_CHECK_ISATTR_TEST_format(
                attr_value_expr=attr_value_expr,
                attr_value_is_valid_expr=attr_value_is_valid_expr,
                local_name_sentinel=local_name_sentinel,
            )
        # Else, this attribute name is qualified (i.e., contains one or more
        # "." delimiters), fallback to a general solution performing iteration.
        else:
            #FIXME: Implement us up when we find the time, please. We currently
            #raise an exception simply because we ran out of time for this. :{
            raise BeartypeValeSubscriptionException(
                f'{get_repr()} first argument '
                f'{repr(attr_name)} not unqualified Python identifier '
                f'(i.e., contains one or more "." characters).'
            )

        # Create and return this subscription.
        return BeartypeValidator(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,
            get_repr=get_repr,
        )
