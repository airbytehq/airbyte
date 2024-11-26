from typing import Collection, List, Optional, Type

from ..error import GraphQLError
from ..language import DocumentNode, ParallelVisitor, visit
from ..type import GraphQLSchema, assert_valid_schema
from ..pyutils import inspect, is_collection
from ..utilities import TypeInfo, TypeInfoVisitor
from .rules import ASTValidationRule
from .specified_rules import specified_rules, specified_sdl_rules
from .validation_context import SDLValidationContext, ValidationContext

__all__ = ["assert_valid_sdl", "assert_valid_sdl_extension", "validate", "validate_sdl"]


class ValidationAbortedError(RuntimeError):
    """Error when a validation has been aborted (error limit reached)."""


def validate(
    schema: GraphQLSchema,
    document_ast: DocumentNode,
    rules: Optional[Collection[Type[ASTValidationRule]]] = None,
    max_errors: Optional[int] = None,
    type_info: Optional[TypeInfo] = None,
) -> List[GraphQLError]:
    """Implements the "Validation" section of the spec.

    Validation runs synchronously, returning a list of encountered errors, or an empty
    list if no errors were encountered and the document is valid.

    A list of specific validation rules may be provided. If not provided, the default
    list of rules defined by the GraphQL specification will be used.

    Each validation rule is a ValidationRule object which is a visitor object that holds
    a ValidationContext (see the language/visitor API). Visitor methods are expected to
    return GraphQLErrors, or lists of GraphQLErrors when invalid.

    Validate will stop validation after a ``max_errors`` limit has been reached.
    Attackers can send pathologically invalid queries to induce a DoS attack,
    so by default ``max_errors`` set to 100 errors.

    Providing a custom TypeInfo instance is deprecated and will be removed in v3.3.
    """
    if not document_ast or not isinstance(document_ast, DocumentNode):
        raise TypeError("Must provide document.")
    # If the schema used for validation is invalid, throw an error.
    assert_valid_schema(schema)
    if max_errors is None:
        max_errors = 100
    elif not isinstance(max_errors, int):
        raise TypeError("The maximum number of errors must be passed as an int.")
    if type_info is None:
        type_info = TypeInfo(schema)
    elif not isinstance(type_info, TypeInfo):
        raise TypeError(f"Not a TypeInfo object: {inspect(type_info)}.")
    if rules is None:
        rules = specified_rules
    elif not is_collection(rules) or not all(
        isinstance(rule, type) and issubclass(rule, ASTValidationRule) for rule in rules
    ):
        raise TypeError(
            "Rules must be specified as a collection of ASTValidationRule subclasses."
        )

    errors: List[GraphQLError] = []

    def on_error(error: GraphQLError) -> None:
        if len(errors) >= max_errors:  # type: ignore
            errors.append(
                GraphQLError(
                    "Too many validation errors, error limit reached."
                    " Validation aborted."
                )
            )
            raise ValidationAbortedError
        errors.append(error)

    context = ValidationContext(schema, document_ast, type_info, on_error)

    # This uses a specialized visitor which runs multiple visitors in parallel,
    # while maintaining the visitor skip and break API.
    visitors = [rule(context) for rule in rules]

    # Visit the whole document with each instance of all provided rules.
    try:
        visit(document_ast, TypeInfoVisitor(type_info, ParallelVisitor(visitors)))
    except ValidationAbortedError:
        pass
    return errors


def validate_sdl(
    document_ast: DocumentNode,
    schema_to_extend: Optional[GraphQLSchema] = None,
    rules: Optional[Collection[Type[ASTValidationRule]]] = None,
) -> List[GraphQLError]:
    """Validate an SDL document.

    For internal use only.
    """
    errors: List[GraphQLError] = []
    context = SDLValidationContext(document_ast, schema_to_extend, errors.append)
    if rules is None:
        rules = specified_sdl_rules
    visitors = [rule(context) for rule in rules]
    visit(document_ast, ParallelVisitor(visitors))
    return errors


def assert_valid_sdl(document_ast: DocumentNode) -> None:
    """Assert document is valid SDL.

    Utility function which asserts a SDL document is valid by throwing an error if it
    is invalid.
    """

    errors = validate_sdl(document_ast)
    if errors:
        raise TypeError("\n\n".join(error.message for error in errors))


def assert_valid_sdl_extension(
    document_ast: DocumentNode, schema: GraphQLSchema
) -> None:
    """Assert document is a valid SDL extension.

    Utility function which asserts a SDL document is valid by throwing an error if it
    is invalid.
    """

    errors = validate_sdl(document_ast, schema)
    if errors:
        raise TypeError("\n\n".join(error.message for error in errors))
