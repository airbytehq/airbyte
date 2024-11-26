"""GraphQL Validation

The :mod:`graphql.validation` package fulfills the Validation phase of fulfilling a
GraphQL result.
"""

from .validate import validate

from .validation_context import (
    ASTValidationContext,
    SDLValidationContext,
    ValidationContext,
)

from .rules import ValidationRule, ASTValidationRule, SDLValidationRule

# All validation rules in the GraphQL Specification.
from .specified_rules import specified_rules

# Spec Section: "Executable Definitions"
from .rules.executable_definitions import ExecutableDefinitionsRule

# Spec Section: "Field Selections on Objects, Interfaces, and Unions Types"
from .rules.fields_on_correct_type import FieldsOnCorrectTypeRule

# Spec Section: "Fragments on Composite Types"
from .rules.fragments_on_composite_types import FragmentsOnCompositeTypesRule

# Spec Section: "Argument Names"
from .rules.known_argument_names import KnownArgumentNamesRule

# Spec Section: "Directives Are Defined"
from .rules.known_directives import KnownDirectivesRule

# Spec Section: "Fragment spread target defined"
from .rules.known_fragment_names import KnownFragmentNamesRule

# Spec Section: "Fragment Spread Type Existence"
from .rules.known_type_names import KnownTypeNamesRule

# Spec Section: "Lone Anonymous Operation"
from .rules.lone_anonymous_operation import LoneAnonymousOperationRule

# Spec Section: "Fragments must not form cycles"
from .rules.no_fragment_cycles import NoFragmentCyclesRule

# Spec Section: "All Variable Used Defined"
from .rules.no_undefined_variables import NoUndefinedVariablesRule

# Spec Section: "Fragments must be used"
from .rules.no_unused_fragments import NoUnusedFragmentsRule

# Spec Section: "All Variables Used"
from .rules.no_unused_variables import NoUnusedVariablesRule

# Spec Section: "Field Selection Merging"
from .rules.overlapping_fields_can_be_merged import OverlappingFieldsCanBeMergedRule

# Spec Section: "Fragment spread is possible"
from .rules.possible_fragment_spreads import PossibleFragmentSpreadsRule

# Spec Section: "Argument Optionality"
from .rules.provided_required_arguments import ProvidedRequiredArgumentsRule

# Spec Section: "Leaf Field Selections"
from .rules.scalar_leafs import ScalarLeafsRule

# Spec Section: "Subscriptions with Single Root Field"
from .rules.single_field_subscriptions import SingleFieldSubscriptionsRule

# Spec Section: "Argument Uniqueness"
from .rules.unique_argument_names import UniqueArgumentNamesRule

# Spec Section: "Directives Are Unique Per Location"
from .rules.unique_directives_per_location import UniqueDirectivesPerLocationRule

# Spec Section: "Fragment Name Uniqueness"
from .rules.unique_fragment_names import UniqueFragmentNamesRule

# Spec Section: "Input Object Field Uniqueness"
from .rules.unique_input_field_names import UniqueInputFieldNamesRule

# Spec Section: "Operation Name Uniqueness"
from .rules.unique_operation_names import UniqueOperationNamesRule

# Spec Section: "Variable Uniqueness"
from .rules.unique_variable_names import UniqueVariableNamesRule

# Spec Section: "Value Type Correctness"
from .rules.values_of_correct_type import ValuesOfCorrectTypeRule

# Spec Section: "Variables are Input Types"
from .rules.variables_are_input_types import VariablesAreInputTypesRule

# Spec Section: "All Variable Usages Are Allowed"
from .rules.variables_in_allowed_position import VariablesInAllowedPositionRule

# SDL-specific validation rules
from .rules.lone_schema_definition import LoneSchemaDefinitionRule
from .rules.unique_operation_types import UniqueOperationTypesRule
from .rules.unique_type_names import UniqueTypeNamesRule
from .rules.unique_enum_value_names import UniqueEnumValueNamesRule
from .rules.unique_field_definition_names import UniqueFieldDefinitionNamesRule
from .rules.unique_argument_definition_names import UniqueArgumentDefinitionNamesRule
from .rules.unique_directive_names import UniqueDirectiveNamesRule
from .rules.possible_type_extensions import PossibleTypeExtensionsRule

# Optional rules not defined by the GraphQL Specification
from .rules.custom.no_deprecated import NoDeprecatedCustomRule
from .rules.custom.no_schema_introspection import NoSchemaIntrospectionCustomRule

__all__ = [
    "validate",
    "ASTValidationContext",
    "ASTValidationRule",
    "SDLValidationContext",
    "SDLValidationRule",
    "ValidationContext",
    "ValidationRule",
    "specified_rules",
    "ExecutableDefinitionsRule",
    "FieldsOnCorrectTypeRule",
    "FragmentsOnCompositeTypesRule",
    "KnownArgumentNamesRule",
    "KnownDirectivesRule",
    "KnownFragmentNamesRule",
    "KnownTypeNamesRule",
    "LoneAnonymousOperationRule",
    "NoFragmentCyclesRule",
    "NoUndefinedVariablesRule",
    "NoUnusedFragmentsRule",
    "NoUnusedVariablesRule",
    "OverlappingFieldsCanBeMergedRule",
    "PossibleFragmentSpreadsRule",
    "ProvidedRequiredArgumentsRule",
    "ScalarLeafsRule",
    "SingleFieldSubscriptionsRule",
    "UniqueArgumentNamesRule",
    "UniqueDirectivesPerLocationRule",
    "UniqueFragmentNamesRule",
    "UniqueInputFieldNamesRule",
    "UniqueOperationNamesRule",
    "UniqueVariableNamesRule",
    "ValuesOfCorrectTypeRule",
    "VariablesAreInputTypesRule",
    "VariablesInAllowedPositionRule",
    "LoneSchemaDefinitionRule",
    "UniqueOperationTypesRule",
    "UniqueTypeNamesRule",
    "UniqueEnumValueNamesRule",
    "UniqueFieldDefinitionNamesRule",
    "UniqueArgumentDefinitionNamesRule",
    "UniqueDirectiveNamesRule",
    "PossibleTypeExtensionsRule",
    "NoDeprecatedCustomRule",
    "NoSchemaIntrospectionCustomRule",
]
