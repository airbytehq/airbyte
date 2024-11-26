"""GraphQL Utilities

The :mod:`graphql.utilities` package contains common useful computations to use with
the GraphQL language and type objects.
"""

# Produce the GraphQL query recommended for a full schema introspection.
from .get_introspection_query import get_introspection_query, IntrospectionQuery

# Get the target Operation from a Document.
from .get_operation_ast import get_operation_ast

# Get the Type for the target Operation AST.
from .get_operation_root_type import get_operation_root_type

# Convert a GraphQLSchema to an IntrospectionQuery.
from .introspection_from_schema import introspection_from_schema

# Build a GraphQLSchema from an introspection result.
from .build_client_schema import build_client_schema

# Build a GraphQLSchema from GraphQL Schema language.
from .build_ast_schema import build_ast_schema, build_schema

# Extend an existing GraphQLSchema from a parsed GraphQL Schema language AST.
from .extend_schema import extend_schema

# Sort a GraphQLSchema.
from .lexicographic_sort_schema import lexicographic_sort_schema

# Print a GraphQLSchema to GraphQL Schema language.
from .print_schema import (
    print_introspection_schema,
    print_schema,
    print_type,
    print_value,  # deprecated
)

# Create a GraphQLType from a GraphQL language AST.
from .type_from_ast import type_from_ast

# Convert a language AST to a dictionary.
from .ast_to_dict import ast_to_dict

# Create a Python value from a GraphQL language AST with a type.
from .value_from_ast import value_from_ast

# Create a Python value from a GraphQL language AST without a type.
from .value_from_ast_untyped import value_from_ast_untyped

# Create a GraphQL language AST from a Python value.
from .ast_from_value import ast_from_value

# A helper to use within recursive-descent visitors which need to be aware of
# the GraphQL type system
from .type_info import TypeInfo, TypeInfoVisitor

# Coerce a Python value to a GraphQL type, or produce errors.
from .coerce_input_value import coerce_input_value

# Concatenate multiple ASTs together.
from .concat_ast import concat_ast

# Separate an AST into an AST per Operation.
from .separate_operations import separate_operations

# Strip characters that are not significant to the validity or execution
# of a GraphQL document.
from .strip_ignored_characters import strip_ignored_characters

# Comparators for types
from .type_comparators import is_equal_type, is_type_sub_type_of, do_types_overlap

# Assert that a string is a valid GraphQL name.
from .assert_valid_name import assert_valid_name, is_valid_name_error

# Compare two GraphQLSchemas and detect breaking changes.
from .find_breaking_changes import (
    BreakingChange,
    BreakingChangeType,
    DangerousChange,
    DangerousChangeType,
    find_breaking_changes,
    find_dangerous_changes,
)

__all__ = [
    "BreakingChange",
    "BreakingChangeType",
    "DangerousChange",
    "DangerousChangeType",
    "IntrospectionQuery",
    "TypeInfo",
    "TypeInfoVisitor",
    "assert_valid_name",
    "ast_from_value",
    "ast_to_dict",
    "build_ast_schema",
    "build_client_schema",
    "build_schema",
    "coerce_input_value",
    "concat_ast",
    "do_types_overlap",
    "extend_schema",
    "find_breaking_changes",
    "find_dangerous_changes",
    "get_introspection_query",
    "get_operation_ast",
    "get_operation_root_type",
    "is_equal_type",
    "is_type_sub_type_of",
    "is_valid_name_error",
    "introspection_from_schema",
    "lexicographic_sort_schema",
    "print_introspection_schema",
    "print_schema",
    "print_type",
    "print_value",
    "separate_operations",
    "strip_ignored_characters",
    "type_from_ast",
    "value_from_ast",
    "value_from_ast_untyped",
]
