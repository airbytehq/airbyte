#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Core unary beartype validators** (i.e., :class:`BeartypeValidator` subclasses
implementing unary operations on a single lower-level beartype validator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta, abstractmethod
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._core._valecore import BeartypeValidator
from beartype.vale._util._valeutiltext import format_diagnosis_line
from beartype._util.text.utiltextmagic import CODE_INDENT_1
from beartype._util.text.utiltextrepr import represent_object

# ....................{ SUPERCLASSES                       }....................
class BeartypeValidatorUnaryABC(BeartypeValidator, metaclass=ABCMeta):
    '''
    Abstract base class of all **beartype binary validator** (i.e., validator
    modifying the boolean truthiness returned by the validation performed by a
    single lower-level beartype validator) subclasses.

    Attributes
    ----------
    _validator_operand : BeartypeValidator
        Lower-level validator operated upon by this higher-level validator.
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
        '_validator_operand',
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        validator_operand: BeartypeValidator,
        **kwargs
    ) -> None:
        '''
        Initialize this validator from the passed metadata.

        Parameters
        ----------
        validator_operand : BeartypeValidator
            Lower-level validator operated upon by this higher-level validator.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this operand is *not* itself a beartype validator.
        '''

        # Callable accepting no arguments returning a machine-readable
        # representation of this binary validator.
        get_repr = lambda: (
            f'{self._operator_symbol}{repr(validator_operand)}')

        # Initialize our superclass with all remaining parameters.
        super().__init__(
            is_valid_code_locals=validator_operand._is_valid_code_locals,
            get_repr=get_repr,
            **kwargs
        )

        # Classify all remaining passed parameters.
        self._validator_operand = validator_operand

    # ..................{ GETTERS                            }..................
    #FIXME: Unit test us up, please.
    def get_diagnosis(
        self,
        *,

        # Mandatory keyword-only parameters.
        obj: object,
        indent_level_outer: str,
        indent_level_inner: str,
        **kwargs
    ) -> str:

        # Line diagnosing this object against this negated parent validator.
        line_outer_prefix = format_diagnosis_line(
            validator_repr='(',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
            is_obj_valid=self.is_valid(obj),
        )

        # Line diagnosing this object against this non-negated child validator
        # with an increased indentation level for readability.
        line_inner_operand = self._validator_operand.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner + CODE_INDENT_1,
            **kwargs
        )

        # Line providing the suffixing ")" delimiter for readability.
        line_outer_suffix = format_diagnosis_line(
            validator_repr=')',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
        )

        # Return these lines concatenated.
        return (
            f'{self._operator_symbol}{line_outer_prefix}\n'
            f'{line_inner_operand}\n'
            f'{line_outer_suffix}'
        )

    # ..................{ ABSTRACT                           }..................
    # Abstract methods required to be concretely implemented by subclasses.

    @property
    @abstractmethod
    def _operator_symbol(self) -> str:
        '''
        Human-readable string embodying the operation performed by this unary
        validator - typically the single-character mathematical sign
        symbolizing this operation.
        '''

        pass

# ....................{ SUBCLASSES                         }....................
class BeartypeValidatorNegation(BeartypeValidatorUnaryABC):
    '''
    **Negation beartype validator** (i.e., validator negating the boolean
    truthiness returned by the validation performed by a lower-level beartype
    validator, typically instantiated and returned by the
    :meth:`BeartypeValidator.__invert__` dunder method of that validator).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, validator_operand: BeartypeValidator) -> None:
        '''
        Initialize this higher-level validator from the passed validator.

        Parameters
        ----------
        validator_operand : BeartypeValidator
            Validator operated upon by this higher-level validator.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this operand is *not* a beartype validator.
        '''

        # Validate the passed operand as sane.
        _validate_operand(self, validator_operand)

        # Initialize our superclass with all remaining parameters.
        super().__init__(
            validator_operand=validator_operand,
            is_valid=lambda obj: not validator_operand.is_valid(obj),
            is_valid_code=f'(not {validator_operand._is_valid_code})',
        )

    # ..................{ PROPERTIES                         }..................
    @property
    def _operator_symbol(self) -> str:
        return '~'

# ....................{ PRIVATE ~ validators               }....................
def _validate_operand(
    self: BeartypeValidatorUnaryABC,
    validator_operand: BeartypeValidator,
) -> None:
    '''
    Validate the passed validator operand as sane.

    Parameters
    ----------
    self : BeartypeValidatorUnaryABC
        Beartype unary validator operating upon this operand.
    validator_operand : BeartypeValidator
        Validator operated upon by this higher-level validator.

    Raises
    ----------
    BeartypeValeSubscriptionException
        If this operand is *not* a beartype validator.
    '''

    #FIXME: Unit test us up, please.
    # If this operand is *NOT* a beartype validator, raise an exception.
    if not isinstance(validator_operand, BeartypeValidator):
        raise BeartypeValeSubscriptionException(
            f'Beartype "{self._operator_symbol}" validator operand '
            f'{represent_object(validator_operand)} not beartype '
            f'validator (i.e., "beartype.vale.Is*[...]" object).'
        )
    # Else, this operand is a beartype validator.
