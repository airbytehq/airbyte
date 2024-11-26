from typing import Tuple, Type

from .rules import ASTValidationRule

# Spec Section: "Executable Definitions"
from .rules.executable_definitions import ExecutableDefinitionsRule

# Spec Section: "Operation Name Uniqueness"
from .rules.unique_operation_names import UniqueOperationNamesRule

# Spec Section: "Lone Anonymous Operation"
from .rules.lone_anonymous_operation import LoneAnonymousOperationRule

# Spec Section: "Subscriptions with Single Root Field"
from .rules.single_field_subscriptions import SingleFieldSubscriptionsRule

# Spec Section: "Fragment Spread Type Existence"
from .rules.known_type_names import KnownTypeNamesRule

# Spec Section: "Fragments on Composite Types"
from .rules.fragments_on_composite_types import FragmentsOnCompositeTypesRule

# Spec Section: "Variables are Input Types"
from .rules.variables_are_input_types import VariablesAreInputTypesRule

# Spec Section: "Leaf Field Selections"
from .rules.scalar_leafs import ScalarLeafsRule

# Spec Section: "Field Selections on Objects, Interfaces, and Unions Types"
from .rules.fields_on_correct_type import FieldsOnCorrectTypeRule

# Spec Section: "Fragment Name Uniqueness"
from .rules.unique_fragment_names import UniqueFragmentNamesRule

# Spec Section: "Fragment spread target defined"
from .rules.known_fragment_names import KnownFragmentNamesRule

# Spec Section: "Fragments must be used"
from .rules.no_unused_fragments import NoUnusedFragmentsRule

# Spec Section: "Fragment spread is possible"
from .rules.possible_fragment_spreads import PossibleFragmentSpreadsRule

# Spec Section: "Fragments must not form cycles"
from .rules.no_fragment_cycles import NoFragmentCyclesRule

# Spec Section: "Variable Uniqueness"
from .rules.unique_variable_names import UniqueVariableNamesRule

# Spec Section: "All Variable Used Defined"
from .rules.no_undefined_variables import NoUndefinedVariablesRule

# Spec Section: "All Variables Used"
from .rules.no_unused_variables import NoUnusedVariablesRule

# Spec Section: "Directives Are Defined"
from .rules.known_directives import KnownDirectivesRule

# Spec Section: "Directives Are Unique Per Location"
from .rules.unique_directives_per_location import UniqueDirectivesPerLocationRule

# Spec Section: "Argument Names"
from .rules.known_argument_names import KnownArgumentNamesRule
from .rules.known_argument_names import KnownArgumentNamesOnDirectivesRule

# Spec Section: "Argument Uniqueness"
from .rules.unique_argument_names import UniqueArgumentNamesRule

# Spec Section: "Value Type Correctness"
from .rules.values_of_correct_type import ValuesOfCorrectTypeRule

# Spec Section: "Argument Optionality"
from .rules.provided_required_arguments import ProvidedRequiredArgumentsRule
from .rules.provided_required_arguments import ProvidedRequiredArgumentsOnDirectivesRule

# Spec Section: "All Variable Usages Are Allowed"
from .rules.variables_in_allowed_position import VariablesInAllowedPositionRule

# Spec Section: "Field Selection Merging"
from .rules.overlapping_fields_can_be_merged import OverlappingFieldsCanBeMergedRule

# Spec Section: "Input Object Field Uniqueness"
from .rules.unique_input_field_names import UniqueInputFieldNamesRule

# Schema definition language:
from .rules.lone_schema_definition import LoneSchemaDefinitionRule
from .rules.unique_operation_types import UniqueOperationTypesRule
from .rules.unique_type_names import UniqueTypeNamesRule
from .rules.unique_enum_value_names import UniqueEnumValueNamesRule
from .rules.unique_field_definition_names import UniqueFieldDefinitionNamesRule
from .rules.unique_argument_definition_names import UniqueArgumentDefinitionNamesRule
from .rules.unique_directive_names import UniqueDirectiveNamesRule
from .rules.possible_type_extensions import PossibleTypeExtensionsRule

__all__ = ["specified_rules", "specified_sdl_rules"]


# This list includes all validation rules defined by the GraphQL spec.
#
# The order of the rules in this list has been adjusted to lead to the
# most clear output when encountering multiple validation errors.

specified_rules: Tuple[Type[ASTValidationRule], ...] = (
    ExecutableDefinitionsRule,
    UniqueOperationNamesRule,
    LoneAnonymousOperationRule,
    SingleFieldSubscriptionsRule,
    KnownTypeNamesRule,
    FragmentsOnCompositeTypesRule,
    VariablesAreInputTypesRule,
    ScalarLeafsRule,
    FieldsOnCorrectTypeRule,
    UniqueFragmentNamesRule,
    KnownFragmentNamesRule,
    NoUnusedFragmentsRule,
    PossibleFragmentSpreadsRule,
    NoFragmentCyclesRule,
    UniqueVariableNamesRule,
    NoUndefinedVariablesRule,
    NoUnusedVariablesRule,
    KnownDirectivesRule,
    UniqueDirectivesPerLocationRule,
    KnownArgumentNamesRule,
    UniqueArgumentNamesRule,
    ValuesOfCorrectTypeRule,
    ProvidedRequiredArgumentsRule,
    VariablesInAllowedPositionRule,
    OverlappingFieldsCanBeMergedRule,
    UniqueInputFieldNamesRule,
)
"""A tuple with all validation rules defined by the GraphQL specification.

The order of the rules in this tuple has been adjusted to lead to the
most clear output when encountering multiple validation errors.
"""

specified_sdl_rules: Tuple[Type[ASTValidationRule], ...] = (
    LoneSchemaDefinitionRule,
    UniqueOperationTypesRule,
    UniqueTypeNamesRule,
    UniqueEnumValueNamesRule,
    UniqueFieldDefinitionNamesRule,
    UniqueArgumentDefinitionNamesRule,
    UniqueDirectiveNamesRule,
    KnownTypeNamesRule,
    KnownDirectivesRule,
    UniqueDirectivesPerLocationRule,
    PossibleTypeExtensionsRule,
    KnownArgumentNamesOnDirectivesRule,
    UniqueArgumentNamesRule,
    UniqueInputFieldNamesRule,
    ProvidedRequiredArgumentsOnDirectivesRule,
)
"""This tuple includes all rules for validating SDL.

For internal use only.
"""
