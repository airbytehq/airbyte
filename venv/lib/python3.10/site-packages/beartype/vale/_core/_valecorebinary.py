#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Core unary beartype validators** (i.e., :class:`BeartypeValidator` subclasses
implementing binary operations on pairs of lower-level beartype validators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta, abstractmethod
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._core._valecore import BeartypeValidator
from beartype.vale._util._valeutiltext import format_diagnosis_line
from beartype._util.kind.utilkinddict import merge_mappings_two
from beartype._util.text.utiltextmagic import CODE_INDENT_1
from beartype._util.text.utiltextrepr import represent_object

# ....................{ SUPERCLASSES                       }....................
class BeartypeValidatorBinaryABC(BeartypeValidator, metaclass=ABCMeta):
    '''
    Abstract base class of all **beartype binary validator** (i.e., validator
    modifying the boolean truthiness returned by the validation performed by a
    pair of lower-level beartype validators) subclasses.

    Attributes
    ----------
    _validator_operand_1 : BeartypeValidator
        First lower-level validator operated upon by this higher-level
        validator.
    _validator_operand_2 : BeartypeValidator
        Second lower-level validator operated upon by this higher-level
        validator.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_validator_operand_1',
        '_validator_operand_2',
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        validator_operand_1: BeartypeValidator,
        validator_operand_2: BeartypeValidator,
        **kwargs
    ) -> None:
        '''
        Initialize this higher-level validator from the passed validators.

        Parameters
        ----------
        validator_operand_1 : BeartypeValidator
            First validator operated upon by this higher-level validator.
        validator_operand_2 : BeartypeValidator
            Second validator operated upon by this higher-level validator.

        All remaining parameters are passed as is to the superclass
        :meth:`BeartypeValidator.__init__` method.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either of these operands are *not* beartype validators.
        '''

        # Locals safely merging the locals required by the code provided by
        # both validators.
        is_valid_code_locals = merge_mappings_two(
            validator_operand_1._is_valid_code_locals,
            validator_operand_2._is_valid_code_locals,
        )

        # Callable accepting no arguments returning a machine-readable
        # representation of this binary validator.
        get_repr = lambda: (
            f'{repr(validator_operand_1)} {self._operator_symbol} '
            f'{repr(validator_operand_2)}'
        )

        # Initialize our superclass with all remaining parameters.
        super().__init__(
            is_valid_code_locals=is_valid_code_locals,  # type: ignore[arg-type]
            get_repr=get_repr,
            **kwargs
        )

        # Classify all remaining parameters.
        self._validator_operand_1 = validator_operand_1
        self._validator_operand_2 = validator_operand_2

    # ..................{ GETTERS                            }..................
    #FIXME: Unit test us up, please.
    #FIXME: Overly verbose for conjunctions involving three or more
    #beartype validators. Contemplate compaction schemes, please. Specifically,
    #we need to detect this condition here and then compact based on that:
    #    # If either of these validators are themselves conjunctions...
    #    if isinstance(self._validator_operand_1, BeartypeValidatorConjunction):
    #       ...
    #    if isinstance(self._validator_operand_2, BeartypeValidatorConjunction):
    #       ...
    def get_diagnosis(
        self,
        *,

        # Mandatory keyword-only parameters.
        obj: object,
        indent_level_outer: str,
        indent_level_inner: str,

        # Optional keyword-only parameters.
        is_shortcircuited: bool = False,
    ) -> str:

        # Innermost indentation level indented one level deeper than the passed
        # innermost indentation level.
        indent_level_inner_nested = indent_level_inner + CODE_INDENT_1

        # Line diagnosing this object against this parent conjunction.
        line_outer_prefix = format_diagnosis_line(
            validator_repr='(',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
            is_obj_valid=self.is_valid(obj),
        )

        # Line diagnosing this object against this first child validator, with
        # an increased indentation level for readability.
        line_inner_operand_1 = self._validator_operand_1.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner_nested,
            is_shortcircuited=is_shortcircuited,
        )

        # If this binary validator has *NOT* already been short-circuited,
        # decide whether this first child validator short-circuits this second
        # child validator with respect to the passed object.
        if not is_shortcircuited:
            is_shortcircuited = self._is_shortcircuited(obj)
        # Else, this binary validator has already been short-circuited (e.g.,
        # due to being embedded in a higher-level parent validator that was
        # short-circuited with respect to the passed object). In this case,
        # preserve this short-circuiting as is.

        # Line diagnosing this object against this second child validator, with
        # an increased indentation level for readability.
        line_inner_operand_2 = self._validator_operand_2.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner_nested,
            is_shortcircuited=is_shortcircuited,
        )

        # Line providing the suffixing ")" delimiter for readability.
        line_outer_suffix = format_diagnosis_line(
            validator_repr=')',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
        )

        # Return these lines concatenated.
        return (
            f'{line_outer_prefix}\n'
            f'{line_inner_operand_1} {self._operator_symbol}\n'
            f'{line_inner_operand_2}\n'
            f'{line_outer_suffix}'
        )

    # ..................{ ABSTRACT                           }..................
    # Abstract methods required to be concretely implemented by subclasses.

    @property
    @abstractmethod
    def _operator_symbol(self) -> str:
        '''
        Human-readable string embodying the operation performed by this binary
        validator - typically the single-character mathematical sign
        symbolizing this operation.
        '''

        pass


    @abstractmethod
    def _is_shortcircuited(self, obj: object) -> bool:
        '''
        ``True`` only if the first child validator short-circuits the second
        child validator underlying this parent validator with respect to the
        passed object.

        In this context, "short-circuits" is in the boolean evaluation sense.
        Specifically, short-circuiting:

        * Occurs when the first child validator either fully satisfies or
          violates this parent validator with respect to the passed object.
        * Implies the second child validator to be safely ignorable with
          respect to the passed object.

        Parameters
        ----------
        obj : object
            Arbitrary object to be diagnosed against this validator.

        Returns
        ----------
        bool
            ``True`` only if this the passed object short-circuits the second
            child operand validator underlying this parent binary validator.
        '''

        pass

# ....................{ SUBCLASSES ~ &                     }....................
class BeartypeValidatorConjunction(BeartypeValidatorBinaryABC):
    '''
    **Beartype conjunction validator** (i.e., validator conjunctively
    evaluating the boolean truthiness returned by the validation performed by a
    pair of lower-level beartype validators, typically instantiated and
    returned by the :meth:`BeartypeValidator.__and__` dunder method of the
    first validator passed the second).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        validator_operand_1: BeartypeValidator,
        validator_operand_2: BeartypeValidator,
    ) -> None:
        '''
        Initialize this higher-level validator from the passed validators.

        Parameters
        ----------
        validator_operand_1 : BeartypeValidator
            First validator operated upon by this higher-level validator.
        validator_operand_2 : BeartypeValidator
            Second validator operated upon by this higher-level validator.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either of these operands are *not* beartype validators.
        '''

        # Validate the passed operands as sane.
        _validate_operands(self, validator_operand_1, validator_operand_2)

        # Initialize our superclass with all remaining parameters.
        super().__init__(
            validator_operand_1=validator_operand_1,
            validator_operand_2=validator_operand_2,
            # Lambda function conjunctively performing both validations.
            is_valid=lambda obj: (
                validator_operand_1.is_valid(obj) and
                validator_operand_2.is_valid(obj)
            ),
            # Code expression conjunctively performing both validations.
            is_valid_code=(
                f'({validator_operand_1._is_valid_code} and '
                f'{validator_operand_2._is_valid_code})'
            ),
        )

    # ..................{ PROPERTIES                         }..................
    @property
    def _operator_symbol(self) -> str:
        return '&'


    def _is_shortcircuited(self, obj: object) -> bool:

        # Return true only if the passed object violates this first child
        # validator. Why? Because if this first child validator is violated,
        # then this parent validator as a whole is violated; no further
        # validation of this second child validator is required.
        return not self._validator_operand_1.is_valid(obj)

# ....................{ SUBCLASSES ~ |                     }....................
class BeartypeValidatorDisjunction(BeartypeValidatorBinaryABC):
    '''
    **Beartype disjunction validator** (i.e., validator disjunctively
    evaluating the boolean truthiness returned by the validation performed by a
    pair of lower-level beartype validators, typically instantiated and
    returned by the :meth:`BeartypeValidator.__and__` dunder method of the
    first validator passed the second).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        validator_operand_1: BeartypeValidator,
        validator_operand_2: BeartypeValidator,
    ) -> None:
        '''
        Initialize this higher-level validator from the passed validators.

        Parameters
        ----------
        validator_operand_1 : BeartypeValidator
            First validator operated upon by this higher-level validator.
        validator_operand_2 : BeartypeValidator
            Second validator operated upon by this higher-level validator.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either of these operands are *not* beartype validators.
        '''

        # Validate the passed operands as sane.
        _validate_operands(self, validator_operand_1, validator_operand_2)

        # Initialize our superclass with all remaining parameters.
        super().__init__(
            validator_operand_1=validator_operand_1,
            validator_operand_2=validator_operand_2,
            # Lambda function disjunctively performing both validations.
            is_valid=lambda obj: (
                validator_operand_1.is_valid(obj) or
                validator_operand_2.is_valid(obj)
            ),
            # Code expression disjunctively performing both validations.
            is_valid_code=(
                f'({validator_operand_1._is_valid_code} or '
                f'{validator_operand_2._is_valid_code})'
            ),
        )

    # ..................{ PROPERTIES                         }..................
    @property
    def _operator_symbol(self) -> str:
        return '|'


    def _is_shortcircuited(self, obj: object) -> bool:

        # Return true only if the passed object satisfies this first child
        # validator. Why? Because if this first child validator is satisfied,
        # then this parent validator as a whole is satisfied; no further
        # validation of this second child validator is required.
        return self._validator_operand_1.is_valid(obj)

# ....................{ PRIVATE ~ validators               }....................
def _validate_operands(
    self: BeartypeValidatorBinaryABC,
    validator_operand_1: BeartypeValidator,
    validator_operand_2: BeartypeValidator,
) -> None:
    '''
    Validate the passed validator operands as sane.

    Parameters
    ----------
    self : BeartypeValidatorBinaryABC
        Beartype binary validator operating upon these operands.
    validator_operand_1 : BeartypeValidator
        First validator operated upon by this higher-level validator.
    validator_operand_2 : BeartypeValidator
        Second validator operated upon by this higher-level validator.

    Raises
    ----------
    BeartypeValeSubscriptionException
        If either of these operands are *not* beartype validators.
    '''

    # If either of these operands are *NOT* beartype validators, raise an
    # exception.
    if not isinstance(validator_operand_1, BeartypeValidator):
        raise BeartypeValeSubscriptionException(
            f'Beartype "{self._operator_symbol}" validator first operand '
            f'{represent_object(validator_operand_1)} not beartype '
            f'validator (i.e., "beartype.vale.Is*[...]" object).'
        )
    elif not isinstance(validator_operand_2, BeartypeValidator):
        raise BeartypeValeSubscriptionException(
            f'Beartype "{self._operator_symbol}" validator second operand '
            f'{represent_object(validator_operand_2)} not beartype '
            f'validator (i.e., "beartype.vale.Is*[...]" object).'
        )
    # Else, both of these operands are beartype validators.
