from typing import Callable, Dict, List, Optional, Union, TypeVar, cast
from functools import partial

from .ast import (
    ArgumentNode,
    BooleanValueNode,
    ConstArgumentNode,
    ConstDirectiveNode,
    ConstValueNode,
    DefinitionNode,
    DirectiveDefinitionNode,
    DirectiveNode,
    DocumentNode,
    EnumTypeDefinitionNode,
    EnumTypeExtensionNode,
    EnumValueDefinitionNode,
    EnumValueNode,
    FieldDefinitionNode,
    FieldNode,
    FloatValueNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    InlineFragmentNode,
    InputObjectTypeDefinitionNode,
    InputObjectTypeExtensionNode,
    InputValueDefinitionNode,
    IntValueNode,
    InterfaceTypeDefinitionNode,
    InterfaceTypeExtensionNode,
    ListTypeNode,
    ListValueNode,
    Location,
    NameNode,
    NamedTypeNode,
    NonNullTypeNode,
    NullValueNode,
    ObjectFieldNode,
    ObjectTypeDefinitionNode,
    ObjectTypeExtensionNode,
    ObjectValueNode,
    OperationDefinitionNode,
    OperationType,
    OperationTypeDefinitionNode,
    ScalarTypeDefinitionNode,
    ScalarTypeExtensionNode,
    SchemaDefinitionNode,
    SchemaExtensionNode,
    SelectionNode,
    SelectionSetNode,
    StringValueNode,
    TypeNode,
    TypeSystemExtensionNode,
    UnionTypeDefinitionNode,
    UnionTypeExtensionNode,
    ValueNode,
    VariableDefinitionNode,
    VariableNode,
)
from .directive_locations import DirectiveLocation
from .ast import Token
from .lexer import Lexer, is_punctuator_token_kind
from .source import Source, is_source
from .token_kind import TokenKind
from ..error import GraphQLError, GraphQLSyntaxError

__all__ = ["parse", "parse_type", "parse_value", "parse_const_value"]

T = TypeVar("T")

SourceType = Union[Source, str]


def parse(
    source: SourceType,
    no_location: bool = False,
    max_tokens: Optional[int] = None,
    allow_legacy_fragment_variables: bool = False,
) -> DocumentNode:
    """Given a GraphQL source, parse it into a Document.

    Throws GraphQLError if a syntax error is encountered.

    By default, the parser creates AST nodes that know the location in the source that
    they correspond to. Setting the ``no_location`` parameter to False disables that
    behavior for performance or testing.

    Parser CPU and memory usage is linear to the number of tokens in a document,
    however in extreme cases it becomes quadratic due to memory exhaustion.
    Parsing happens before validation, so even invalid queries can burn lots of
    CPU time and memory. To prevent this, you can set a maximum number of tokens
    allowed within a document using the ``max_tokens`` parameter.

    Legacy feature (will be removed in v3.3):

    If ``allow_legacy_fragment_variables`` is set to ``True``, the parser will
    understand and parse variable definitions contained in a fragment definition.
    They'll be represented in the
    :attr:`~graphql.language.FragmentDefinitionNode.variable_definitions` field
    of the :class:`~graphql.language.FragmentDefinitionNode`.

    The syntax is identical to normal, query-defined variables. For example::

        fragment A($var: Boolean = false) on T  {
          ...
        }
    """
    parser = Parser(
        source,
        no_location=no_location,
        max_tokens=max_tokens,
        allow_legacy_fragment_variables=allow_legacy_fragment_variables,
    )
    return parser.parse_document()


def parse_value(
    source: SourceType,
    no_location: bool = False,
    max_tokens: Optional[int] = None,
    allow_legacy_fragment_variables: bool = False,
) -> ValueNode:
    """Parse the AST for a given string containing a GraphQL value.

    Throws GraphQLError if a syntax error is encountered.

    This is useful within tools that operate upon GraphQL Values directly and in
    isolation of complete GraphQL documents.

    Consider providing the results to the utility function:
    :func:`~graphql.utilities.value_from_ast`.
    """
    parser = Parser(
        source,
        no_location=no_location,
        max_tokens=max_tokens,
        allow_legacy_fragment_variables=allow_legacy_fragment_variables,
    )
    parser.expect_token(TokenKind.SOF)
    value = parser.parse_value_literal(False)
    parser.expect_token(TokenKind.EOF)
    return value


def parse_const_value(
    source: SourceType,
    no_location: bool = False,
    max_tokens: Optional[int] = None,
    allow_legacy_fragment_variables: bool = False,
) -> ConstValueNode:
    """Parse the AST for a given string containing a GraphQL constant value.

    Similar to parse_value, but raises a arse error if it encounters a variable.
    The return type will be a constant value.
    """
    parser = Parser(
        source,
        no_location=no_location,
        max_tokens=max_tokens,
        allow_legacy_fragment_variables=allow_legacy_fragment_variables,
    )
    parser.expect_token(TokenKind.SOF)
    value = parser.parse_const_value_literal()
    parser.expect_token(TokenKind.EOF)
    return value


def parse_type(
    source: SourceType,
    no_location: bool = False,
    max_tokens: Optional[int] = None,
    allow_legacy_fragment_variables: bool = False,
) -> TypeNode:
    """Parse the AST for a given string containing a GraphQL Type.

    Throws GraphQLError if a syntax error is encountered.

    This is useful within tools that operate upon GraphQL Types directly and
    in isolation of complete GraphQL documents.

    Consider providing the results to the utility function:
    :func:`~graphql.utilities.value_from_ast`.
    """
    parser = Parser(
        source,
        no_location=no_location,
        max_tokens=max_tokens,
        allow_legacy_fragment_variables=allow_legacy_fragment_variables,
    )
    parser.expect_token(TokenKind.SOF)
    type_ = parser.parse_type_reference()
    parser.expect_token(TokenKind.EOF)
    return type_


class Parser:
    """GraphQL AST parser.

    This class is exported only to assist people in implementing their own parsers
    without duplicating too much code and should be used only as last resort for cases
    such as experimental syntax or if certain features couldn't be contributed upstream.

    It's still part of the internal API and is versioned, so any changes to it are never
    considered breaking changes. If you still need to support multiple versions of the
    library, please use the `__version_info__` variable for version detection.
    """

    _lexer: Lexer
    _no_location: bool
    _max_tokens: Optional[int]
    _allow_legacy_fragment_variables: bool
    _token_counter: int

    def __init__(
        self,
        source: SourceType,
        no_location: bool = False,
        max_tokens: Optional[int] = None,
        allow_legacy_fragment_variables: bool = False,
    ):
        source = (
            cast(Source, source) if is_source(source) else Source(cast(str, source))
        )

        self._lexer = Lexer(source)
        self._no_location = no_location
        self._max_tokens = max_tokens
        self._allow_legacy_fragment_variables = allow_legacy_fragment_variables
        self._token_counter = 0

    def parse_name(self) -> NameNode:
        """Convert a name lex token into a name parse node."""
        token = self.expect_token(TokenKind.NAME)
        return NameNode(value=token.value, loc=self.loc(token))

    # Implement the parsing rules in the Document section.

    def parse_document(self) -> DocumentNode:
        """Document: Definition+"""
        start = self._lexer.token
        return DocumentNode(
            definitions=self.many(TokenKind.SOF, self.parse_definition, TokenKind.EOF),
            loc=self.loc(start),
        )

    _parse_type_system_definition_method_names: Dict[str, str] = {
        "schema": "schema_definition",
        "scalar": "scalar_type_definition",
        "type": "object_type_definition",
        "interface": "interface_type_definition",
        "union": "union_type_definition",
        "enum": "enum_type_definition",
        "input": "input_object_type_definition",
        "directive": "directive_definition",
    }

    _parse_other_definition_method_names: Dict[str, str] = {
        **dict.fromkeys(("query", "mutation", "subscription"), "operation_definition"),
        "fragment": "fragment_definition",
        "extend": "type_system_extension",
    }

    def parse_definition(self) -> DefinitionNode:
        """Definition: ExecutableDefinition or TypeSystemDefinition/Extension

        ExecutableDefinition: OperationDefinition or FragmentDefinition

        TypeSystemDefinition: SchemaDefinition, TypeDefinition or DirectiveDefinition

        TypeDefinition: ScalarTypeDefinition, ObjectTypeDefinition,
            InterfaceTypeDefinition, UnionTypeDefinition,
            EnumTypeDefinition or InputObjectTypeDefinition
        """
        if self.peek(TokenKind.BRACE_L):
            return self.parse_operation_definition()

        # Many definitions begin with a description and require a lookahead.
        has_description = self.peek_description()
        keyword_token = (
            self._lexer.lookahead() if has_description else self._lexer.token
        )

        if keyword_token.kind is TokenKind.NAME:
            token_name = cast(str, keyword_token.value)
            method_name = self._parse_type_system_definition_method_names.get(
                token_name
            )
            if method_name:
                return getattr(self, f"parse_{method_name}")()

            if has_description:
                raise GraphQLSyntaxError(
                    self._lexer.source,
                    self._lexer.token.start,
                    "Unexpected description,"
                    " descriptions are supported only on type definitions.",
                )

            method_name = self._parse_other_definition_method_names.get(token_name)
            if method_name:
                return getattr(self, f"parse_{method_name}")()

        raise self.unexpected(keyword_token)

    # Implement the parsing rules in the Operations section.

    def parse_operation_definition(self) -> OperationDefinitionNode:
        """OperationDefinition"""
        start = self._lexer.token
        if self.peek(TokenKind.BRACE_L):
            return OperationDefinitionNode(
                operation=OperationType.QUERY,
                name=None,
                variable_definitions=[],
                directives=[],
                selection_set=self.parse_selection_set(),
                loc=self.loc(start),
            )
        operation = self.parse_operation_type()
        name = self.parse_name() if self.peek(TokenKind.NAME) else None
        return OperationDefinitionNode(
            operation=operation,
            name=name,
            variable_definitions=self.parse_variable_definitions(),
            directives=self.parse_directives(False),
            selection_set=self.parse_selection_set(),
            loc=self.loc(start),
        )

    def parse_operation_type(self) -> OperationType:
        """OperationType: one of query mutation subscription"""
        operation_token = self.expect_token(TokenKind.NAME)
        try:
            return OperationType(operation_token.value)
        except ValueError:
            raise self.unexpected(operation_token)

    def parse_variable_definitions(self) -> List[VariableDefinitionNode]:
        """VariableDefinitions: (VariableDefinition+)"""
        return self.optional_many(
            TokenKind.PAREN_L, self.parse_variable_definition, TokenKind.PAREN_R
        )

    def parse_variable_definition(self) -> VariableDefinitionNode:
        """VariableDefinition: Variable: Type DefaultValue? Directives[Const]?"""
        start = self._lexer.token
        return VariableDefinitionNode(
            variable=self.parse_variable(),
            type=self.expect_token(TokenKind.COLON) and self.parse_type_reference(),
            default_value=self.parse_const_value_literal()
            if self.expect_optional_token(TokenKind.EQUALS)
            else None,
            directives=self.parse_const_directives(),
            loc=self.loc(start),
        )

    def parse_variable(self) -> VariableNode:
        """Variable: $Name"""
        start = self._lexer.token
        self.expect_token(TokenKind.DOLLAR)
        return VariableNode(name=self.parse_name(), loc=self.loc(start))

    def parse_selection_set(self) -> SelectionSetNode:
        """SelectionSet: {Selection+}"""
        start = self._lexer.token
        return SelectionSetNode(
            selections=self.many(
                TokenKind.BRACE_L, self.parse_selection, TokenKind.BRACE_R
            ),
            loc=self.loc(start),
        )

    def parse_selection(self) -> SelectionNode:
        """Selection: Field or FragmentSpread or InlineFragment"""
        return (
            self.parse_fragment if self.peek(TokenKind.SPREAD) else self.parse_field
        )()

    def parse_field(self) -> FieldNode:
        """Field: Alias? Name Arguments? Directives? SelectionSet?"""
        start = self._lexer.token
        name_or_alias = self.parse_name()
        if self.expect_optional_token(TokenKind.COLON):
            alias: Optional[NameNode] = name_or_alias
            name = self.parse_name()
        else:
            alias = None
            name = name_or_alias
        return FieldNode(
            alias=alias,
            name=name,
            arguments=self.parse_arguments(False),
            directives=self.parse_directives(False),
            selection_set=self.parse_selection_set()
            if self.peek(TokenKind.BRACE_L)
            else None,
            loc=self.loc(start),
        )

    def parse_arguments(self, is_const: bool) -> List[ArgumentNode]:
        """Arguments[Const]: (Argument[?Const]+)"""
        item = self.parse_const_argument if is_const else self.parse_argument
        item = cast(Callable[[], ArgumentNode], item)
        return self.optional_many(TokenKind.PAREN_L, item, TokenKind.PAREN_R)

    def parse_argument(self, is_const: bool = False) -> ArgumentNode:
        """Argument[Const]: Name : Value[?Const]"""
        start = self._lexer.token
        name = self.parse_name()

        self.expect_token(TokenKind.COLON)
        return ArgumentNode(
            name=name, value=self.parse_value_literal(is_const), loc=self.loc(start)
        )

    def parse_const_argument(self) -> ConstArgumentNode:
        """Argument[Const]: Name : Value[Const]"""
        return cast(ConstArgumentNode, self.parse_argument(True))

    # Implement the parsing rules in the Fragments section.

    def parse_fragment(self) -> Union[FragmentSpreadNode, InlineFragmentNode]:
        """Corresponds to both FragmentSpread and InlineFragment in the spec.

        FragmentSpread: ... FragmentName Directives?
        InlineFragment: ... TypeCondition? Directives? SelectionSet
        """
        start = self._lexer.token
        self.expect_token(TokenKind.SPREAD)

        has_type_condition = self.expect_optional_keyword("on")
        if not has_type_condition and self.peek(TokenKind.NAME):
            return FragmentSpreadNode(
                name=self.parse_fragment_name(),
                directives=self.parse_directives(False),
                loc=self.loc(start),
            )
        return InlineFragmentNode(
            type_condition=self.parse_named_type() if has_type_condition else None,
            directives=self.parse_directives(False),
            selection_set=self.parse_selection_set(),
            loc=self.loc(start),
        )

    def parse_fragment_definition(self) -> FragmentDefinitionNode:
        """FragmentDefinition"""
        start = self._lexer.token
        self.expect_keyword("fragment")
        # Legacy support for defining variables within fragments changes
        # the grammar of FragmentDefinition
        if self._allow_legacy_fragment_variables:
            return FragmentDefinitionNode(
                name=self.parse_fragment_name(),
                variable_definitions=self.parse_variable_definitions(),
                type_condition=self.parse_type_condition(),
                directives=self.parse_directives(False),
                selection_set=self.parse_selection_set(),
                loc=self.loc(start),
            )
        return FragmentDefinitionNode(
            name=self.parse_fragment_name(),
            type_condition=self.parse_type_condition(),
            directives=self.parse_directives(False),
            selection_set=self.parse_selection_set(),
            loc=self.loc(start),
        )

    def parse_fragment_name(self) -> NameNode:
        """FragmentName: Name but not ``on``"""
        if self._lexer.token.value == "on":
            raise self.unexpected()
        return self.parse_name()

    def parse_type_condition(self) -> NamedTypeNode:
        """TypeCondition: NamedType"""
        self.expect_keyword("on")
        return self.parse_named_type()

    # Implement the parsing rules in the Values section.

    _parse_value_literal_method_names: Dict[TokenKind, str] = {
        TokenKind.BRACKET_L: "list",
        TokenKind.BRACE_L: "object",
        TokenKind.INT: "int",
        TokenKind.FLOAT: "float",
        TokenKind.STRING: "string_literal",
        TokenKind.BLOCK_STRING: "string_literal",
        TokenKind.NAME: "named_values",
        TokenKind.DOLLAR: "variable_value",
    }

    def parse_value_literal(self, is_const: bool) -> ValueNode:
        method_name = self._parse_value_literal_method_names.get(self._lexer.token.kind)
        if method_name:  # pragma: no cover
            return getattr(self, f"parse_{method_name}")(is_const)
        raise self.unexpected()  # pragma: no cover

    def parse_string_literal(self, _is_const: bool = False) -> StringValueNode:
        token = self._lexer.token
        self.advance_lexer()
        return StringValueNode(
            value=token.value,
            block=token.kind == TokenKind.BLOCK_STRING,
            loc=self.loc(token),
        )

    def parse_list(self, is_const: bool) -> ListValueNode:
        """ListValue[Const]"""
        start = self._lexer.token
        item = partial(self.parse_value_literal, is_const)
        # noinspection PyTypeChecker
        return ListValueNode(
            values=self.any(TokenKind.BRACKET_L, item, TokenKind.BRACKET_R),
            loc=self.loc(start),
        )

    def parse_object_field(self, is_const: bool) -> ObjectFieldNode:
        start = self._lexer.token
        name = self.parse_name()
        self.expect_token(TokenKind.COLON)

        return ObjectFieldNode(
            name=name, value=self.parse_value_literal(is_const), loc=self.loc(start)
        )

    def parse_object(self, is_const: bool) -> ObjectValueNode:
        """ObjectValue[Const]"""
        start = self._lexer.token
        item = partial(self.parse_object_field, is_const)
        return ObjectValueNode(
            fields=self.any(TokenKind.BRACE_L, item, TokenKind.BRACE_R),
            loc=self.loc(start),
        )

    def parse_int(self, _is_const: bool = False) -> IntValueNode:
        token = self._lexer.token
        self.advance_lexer()
        return IntValueNode(value=token.value, loc=self.loc(token))

    def parse_float(self, _is_const: bool = False) -> FloatValueNode:
        token = self._lexer.token
        self.advance_lexer()
        return FloatValueNode(value=token.value, loc=self.loc(token))

    def parse_named_values(self, _is_const: bool = False) -> ValueNode:
        token = self._lexer.token
        value = token.value
        self.advance_lexer()
        if value == "true":
            return BooleanValueNode(value=True, loc=self.loc(token))
        if value == "false":
            return BooleanValueNode(value=False, loc=self.loc(token))
        if value == "null":
            return NullValueNode(loc=self.loc(token))
        return EnumValueNode(value=value, loc=self.loc(token))

    def parse_variable_value(self, is_const: bool) -> VariableNode:
        if is_const:
            variable_token = self.expect_token(TokenKind.DOLLAR)
            token = self._lexer.token
            if token.kind is TokenKind.NAME:
                var_name = token.value
                raise GraphQLSyntaxError(
                    self._lexer.source,
                    variable_token.start,
                    f"Unexpected variable '${var_name}' in constant value.",
                )
            raise self.unexpected(variable_token)
        return self.parse_variable()

    def parse_const_value_literal(self) -> ConstValueNode:
        return cast(ConstValueNode, self.parse_value_literal(True))

    # Implement the parsing rules in the Directives section.

    def parse_directives(self, is_const: bool) -> List[DirectiveNode]:
        """Directives[Const]: Directive[?Const]+"""
        directives: List[DirectiveNode] = []
        append = directives.append
        while self.peek(TokenKind.AT):
            append(self.parse_directive(is_const))
        return directives

    def parse_const_directives(self) -> List[ConstDirectiveNode]:
        return cast(List[ConstDirectiveNode], self.parse_directives(True))

    def parse_directive(self, is_const: bool) -> DirectiveNode:
        """Directive[Const]: @ Name Arguments[?Const]?"""
        start = self._lexer.token
        self.expect_token(TokenKind.AT)
        return DirectiveNode(
            name=self.parse_name(),
            arguments=self.parse_arguments(is_const),
            loc=self.loc(start),
        )

    # Implement the parsing rules in the Types section.

    def parse_type_reference(self) -> TypeNode:
        """Type: NamedType or ListType or NonNullType"""
        start = self._lexer.token
        type_: TypeNode
        if self.expect_optional_token(TokenKind.BRACKET_L):
            inner_type = self.parse_type_reference()
            self.expect_token(TokenKind.BRACKET_R)
            type_ = ListTypeNode(type=inner_type, loc=self.loc(start))
        else:
            type_ = self.parse_named_type()
        if self.expect_optional_token(TokenKind.BANG):
            return NonNullTypeNode(type=type_, loc=self.loc(start))
        return type_

    def parse_named_type(self) -> NamedTypeNode:
        """NamedType: Name"""
        start = self._lexer.token
        return NamedTypeNode(name=self.parse_name(), loc=self.loc(start))

    # Implement the parsing rules in the Type Definition section.

    _parse_type_extension_method_names: Dict[str, str] = {
        "schema": "schema_extension",
        "scalar": "scalar_type_extension",
        "type": "object_type_extension",
        "interface": "interface_type_extension",
        "union": "union_type_extension",
        "enum": "enum_type_extension",
        "input": "input_object_type_extension",
    }

    def parse_type_system_extension(self) -> TypeSystemExtensionNode:
        """TypeSystemExtension"""
        keyword_token = self._lexer.lookahead()
        if keyword_token.kind == TokenKind.NAME:
            method_name = self._parse_type_extension_method_names.get(
                cast(str, keyword_token.value)
            )
            if method_name:  # pragma: no cover
                return getattr(self, f"parse_{method_name}")()
        raise self.unexpected(keyword_token)

    def peek_description(self) -> bool:
        return self.peek(TokenKind.STRING) or self.peek(TokenKind.BLOCK_STRING)

    def parse_description(self) -> Optional[StringValueNode]:
        """Description: StringValue"""
        if self.peek_description():
            return self.parse_string_literal()
        return None

    def parse_schema_definition(self) -> SchemaDefinitionNode:
        """SchemaDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("schema")
        directives = self.parse_const_directives()
        operation_types = self.many(
            TokenKind.BRACE_L, self.parse_operation_type_definition, TokenKind.BRACE_R
        )
        return SchemaDefinitionNode(
            description=description,
            directives=directives,
            operation_types=operation_types,
            loc=self.loc(start),
        )

    def parse_operation_type_definition(self) -> OperationTypeDefinitionNode:
        """OperationTypeDefinition: OperationType : NamedType"""
        start = self._lexer.token
        operation = self.parse_operation_type()
        self.expect_token(TokenKind.COLON)
        type_ = self.parse_named_type()
        return OperationTypeDefinitionNode(
            operation=operation, type=type_, loc=self.loc(start)
        )

    def parse_scalar_type_definition(self) -> ScalarTypeDefinitionNode:
        """ScalarTypeDefinition: Description? scalar Name Directives[Const]?"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("scalar")
        name = self.parse_name()
        directives = self.parse_const_directives()
        return ScalarTypeDefinitionNode(
            description=description,
            name=name,
            directives=directives,
            loc=self.loc(start),
        )

    def parse_object_type_definition(self) -> ObjectTypeDefinitionNode:
        """ObjectTypeDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("type")
        name = self.parse_name()
        interfaces = self.parse_implements_interfaces()
        directives = self.parse_const_directives()
        fields = self.parse_fields_definition()
        return ObjectTypeDefinitionNode(
            description=description,
            name=name,
            interfaces=interfaces,
            directives=directives,
            fields=fields,
            loc=self.loc(start),
        )

    def parse_implements_interfaces(self) -> List[NamedTypeNode]:
        """ImplementsInterfaces"""
        return (
            self.delimited_many(TokenKind.AMP, self.parse_named_type)
            if self.expect_optional_keyword("implements")
            else []
        )

    def parse_fields_definition(self) -> List[FieldDefinitionNode]:
        """FieldsDefinition: {FieldDefinition+}"""
        return self.optional_many(
            TokenKind.BRACE_L, self.parse_field_definition, TokenKind.BRACE_R
        )

    def parse_field_definition(self) -> FieldDefinitionNode:
        """FieldDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        name = self.parse_name()
        args = self.parse_argument_defs()
        self.expect_token(TokenKind.COLON)
        type_ = self.parse_type_reference()
        directives = self.parse_const_directives()
        return FieldDefinitionNode(
            description=description,
            name=name,
            arguments=args,
            type=type_,
            directives=directives,
            loc=self.loc(start),
        )

    def parse_argument_defs(self) -> List[InputValueDefinitionNode]:
        """ArgumentsDefinition: (InputValueDefinition+)"""
        return self.optional_many(
            TokenKind.PAREN_L, self.parse_input_value_def, TokenKind.PAREN_R
        )

    def parse_input_value_def(self) -> InputValueDefinitionNode:
        """InputValueDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        name = self.parse_name()
        self.expect_token(TokenKind.COLON)
        type_ = self.parse_type_reference()
        default_value = (
            self.parse_const_value_literal()
            if self.expect_optional_token(TokenKind.EQUALS)
            else None
        )
        directives = self.parse_const_directives()
        return InputValueDefinitionNode(
            description=description,
            name=name,
            type=type_,
            default_value=default_value,
            directives=directives,
            loc=self.loc(start),
        )

    def parse_interface_type_definition(self) -> InterfaceTypeDefinitionNode:
        """InterfaceTypeDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("interface")
        name = self.parse_name()
        interfaces = self.parse_implements_interfaces()
        directives = self.parse_const_directives()
        fields = self.parse_fields_definition()
        return InterfaceTypeDefinitionNode(
            description=description,
            name=name,
            interfaces=interfaces,
            directives=directives,
            fields=fields,
            loc=self.loc(start),
        )

    def parse_union_type_definition(self) -> UnionTypeDefinitionNode:
        """UnionTypeDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("union")
        name = self.parse_name()
        directives = self.parse_const_directives()
        types = self.parse_union_member_types()
        return UnionTypeDefinitionNode(
            description=description,
            name=name,
            directives=directives,
            types=types,
            loc=self.loc(start),
        )

    def parse_union_member_types(self) -> List[NamedTypeNode]:
        """UnionMemberTypes"""
        return (
            self.delimited_many(TokenKind.PIPE, self.parse_named_type)
            if self.expect_optional_token(TokenKind.EQUALS)
            else []
        )

    def parse_enum_type_definition(self) -> EnumTypeDefinitionNode:
        """UnionTypeDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("enum")
        name = self.parse_name()
        directives = self.parse_const_directives()
        values = self.parse_enum_values_definition()
        return EnumTypeDefinitionNode(
            description=description,
            name=name,
            directives=directives,
            values=values,
            loc=self.loc(start),
        )

    def parse_enum_values_definition(self) -> List[EnumValueDefinitionNode]:
        """EnumValuesDefinition: {EnumValueDefinition+}"""
        return self.optional_many(
            TokenKind.BRACE_L, self.parse_enum_value_definition, TokenKind.BRACE_R
        )

    def parse_enum_value_definition(self) -> EnumValueDefinitionNode:
        """EnumValueDefinition: Description? EnumValue Directives[Const]?"""
        start = self._lexer.token
        description = self.parse_description()
        name = self.parse_enum_value_name()
        directives = self.parse_const_directives()
        return EnumValueDefinitionNode(
            description=description,
            name=name,
            directives=directives,
            loc=self.loc(start),
        )

    def parse_enum_value_name(self) -> NameNode:
        """EnumValue: Name but not ``true``, ``false`` or ``null``"""
        if self._lexer.token.value in ("true", "false", "null"):
            raise GraphQLSyntaxError(
                self._lexer.source,
                self._lexer.token.start,
                f"{get_token_desc(self._lexer.token)} is reserved"
                " and cannot be used for an enum value.",
            )
        return self.parse_name()

    def parse_input_object_type_definition(self) -> InputObjectTypeDefinitionNode:
        """InputObjectTypeDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("input")
        name = self.parse_name()
        directives = self.parse_const_directives()
        fields = self.parse_input_fields_definition()
        return InputObjectTypeDefinitionNode(
            description=description,
            name=name,
            directives=directives,
            fields=fields,
            loc=self.loc(start),
        )

    def parse_input_fields_definition(self) -> List[InputValueDefinitionNode]:
        """InputFieldsDefinition: {InputValueDefinition+}"""
        return self.optional_many(
            TokenKind.BRACE_L, self.parse_input_value_def, TokenKind.BRACE_R
        )

    def parse_schema_extension(self) -> SchemaExtensionNode:
        """SchemaExtension"""
        start = self._lexer.token
        self.expect_keyword("extend")
        self.expect_keyword("schema")
        directives = self.parse_const_directives()
        operation_types = self.optional_many(
            TokenKind.BRACE_L, self.parse_operation_type_definition, TokenKind.BRACE_R
        )
        if not directives and not operation_types:
            raise self.unexpected()
        return SchemaExtensionNode(
            directives=directives, operation_types=operation_types, loc=self.loc(start)
        )

    def parse_scalar_type_extension(self) -> ScalarTypeExtensionNode:
        """ScalarTypeExtension"""
        start = self._lexer.token
        self.expect_keyword("extend")
        self.expect_keyword("scalar")
        name = self.parse_name()
        directives = self.parse_const_directives()
        if not directives:
            raise self.unexpected()
        return ScalarTypeExtensionNode(
            name=name, directives=directives, loc=self.loc(start)
        )

    def parse_object_type_extension(self) -> ObjectTypeExtensionNode:
        """ObjectTypeExtension"""
        start = self._lexer.token
        self.expect_keyword("extend")
        self.expect_keyword("type")
        name = self.parse_name()
        interfaces = self.parse_implements_interfaces()
        directives = self.parse_const_directives()
        fields = self.parse_fields_definition()
        if not (interfaces or directives or fields):
            raise self.unexpected()
        return ObjectTypeExtensionNode(
            name=name,
            interfaces=interfaces,
            directives=directives,
            fields=fields,
            loc=self.loc(start),
        )

    def parse_interface_type_extension(self) -> InterfaceTypeExtensionNode:
        """InterfaceTypeExtension"""
        start = self._lexer.token
        self.expect_keyword("extend")
        self.expect_keyword("interface")
        name = self.parse_name()
        interfaces = self.parse_implements_interfaces()
        directives = self.parse_const_directives()
        fields = self.parse_fields_definition()
        if not (interfaces or directives or fields):
            raise self.unexpected()
        return InterfaceTypeExtensionNode(
            name=name,
            interfaces=interfaces,
            directives=directives,
            fields=fields,
            loc=self.loc(start),
        )

    def parse_union_type_extension(self) -> UnionTypeExtensionNode:
        """UnionTypeExtension"""
        start = self._lexer.token
        self.expect_keyword("extend")
        self.expect_keyword("union")
        name = self.parse_name()
        directives = self.parse_const_directives()
        types = self.parse_union_member_types()
        if not (directives or types):
            raise self.unexpected()
        return UnionTypeExtensionNode(
            name=name, directives=directives, types=types, loc=self.loc(start)
        )

    def parse_enum_type_extension(self) -> EnumTypeExtensionNode:
        """EnumTypeExtension"""
        start = self._lexer.token
        self.expect_keyword("extend")
        self.expect_keyword("enum")
        name = self.parse_name()
        directives = self.parse_const_directives()
        values = self.parse_enum_values_definition()
        if not (directives or values):
            raise self.unexpected()
        return EnumTypeExtensionNode(
            name=name, directives=directives, values=values, loc=self.loc(start)
        )

    def parse_input_object_type_extension(self) -> InputObjectTypeExtensionNode:
        """InputObjectTypeExtension"""
        start = self._lexer.token
        self.expect_keyword("extend")
        self.expect_keyword("input")
        name = self.parse_name()
        directives = self.parse_const_directives()
        fields = self.parse_input_fields_definition()
        if not (directives or fields):
            raise self.unexpected()
        return InputObjectTypeExtensionNode(
            name=name, directives=directives, fields=fields, loc=self.loc(start)
        )

    def parse_directive_definition(self) -> DirectiveDefinitionNode:
        """DirectiveDefinition"""
        start = self._lexer.token
        description = self.parse_description()
        self.expect_keyword("directive")
        self.expect_token(TokenKind.AT)
        name = self.parse_name()
        args = self.parse_argument_defs()
        repeatable = self.expect_optional_keyword("repeatable")
        self.expect_keyword("on")
        locations = self.parse_directive_locations()
        return DirectiveDefinitionNode(
            description=description,
            name=name,
            arguments=args,
            repeatable=repeatable,
            locations=locations,
            loc=self.loc(start),
        )

    def parse_directive_locations(self) -> List[NameNode]:
        """DirectiveLocations"""
        return self.delimited_many(TokenKind.PIPE, self.parse_directive_location)

    def parse_directive_location(self) -> NameNode:
        """DirectiveLocation"""
        start = self._lexer.token
        name = self.parse_name()
        if name.value in DirectiveLocation.__members__:
            return name
        raise self.unexpected(start)

    # Core parsing utility functions

    def loc(self, start_token: Token) -> Optional[Location]:
        """Return a location object.

        Used to identify the place in the source that created a given parsed object.
        """
        if not self._no_location:
            end_token = self._lexer.last_token
            source = self._lexer.source
            return Location(start_token, end_token, source)
        return None

    def peek(self, kind: TokenKind) -> bool:
        """Determine if the next token is of a given kind"""
        return self._lexer.token.kind == kind

    def expect_token(self, kind: TokenKind) -> Token:
        """Expect the next token to be of the given kind.

        If the next token is of the given kind, return that token after advancing the
        lexer. Otherwise, do not change the parser state and throw an error.
        """
        token = self._lexer.token
        if token.kind == kind:
            self.advance_lexer()
            return token

        raise GraphQLSyntaxError(
            self._lexer.source,
            token.start,
            f"Expected {get_token_kind_desc(kind)}, found {get_token_desc(token)}.",
        )

    def expect_optional_token(self, kind: TokenKind) -> bool:
        """Expect the next token optionally to be of the given kind.

        If the next token is of the given kind, return True after advancing the lexer.
        Otherwise, do not change the parser state and return False.
        """
        token = self._lexer.token
        if token.kind == kind:
            self.advance_lexer()
            return True

        return False

    def expect_keyword(self, value: str) -> None:
        """Expect the next token to be a given keyword.

        If the next token is a given keyword, advance the lexer.
        Otherwise, do not change the parser state and throw an error.
        """
        token = self._lexer.token
        if token.kind == TokenKind.NAME and token.value == value:
            self.advance_lexer()
        else:
            raise GraphQLSyntaxError(
                self._lexer.source,
                token.start,
                f"Expected '{value}', found {get_token_desc(token)}.",
            )

    def expect_optional_keyword(self, value: str) -> bool:
        """Expect the next token optionally to be a given keyword.

        If the next token is a given keyword, return True after advancing the lexer.
        Otherwise, do not change the parser state and return False.
        """
        token = self._lexer.token
        if token.kind == TokenKind.NAME and token.value == value:
            self.advance_lexer()
            return True

        return False

    def unexpected(self, at_token: Optional[Token] = None) -> GraphQLError:
        """Create an error when an unexpected lexed token is encountered."""
        token = at_token or self._lexer.token
        return GraphQLSyntaxError(
            self._lexer.source, token.start, f"Unexpected {get_token_desc(token)}."
        )

    def any(
        self, open_kind: TokenKind, parse_fn: Callable[[], T], close_kind: TokenKind
    ) -> List[T]:
        """Fetch any matching nodes, possibly none.

        Returns a possibly empty list of parse nodes, determined by the ``parse_fn``.
        This list begins with a lex token of ``open_kind`` and ends with a lex token of
        ``close_kind``. Advances the parser to the next lex token after the closing
        token.
        """
        self.expect_token(open_kind)
        nodes: List[T] = []
        append = nodes.append
        expect_optional_token = partial(self.expect_optional_token, close_kind)
        while not expect_optional_token():
            append(parse_fn())
        return nodes

    def optional_many(
        self, open_kind: TokenKind, parse_fn: Callable[[], T], close_kind: TokenKind
    ) -> List[T]:
        """Fetch matching nodes, maybe none.

        Returns a list of parse nodes, determined by the ``parse_fn``. It can be empty
        only if the open token is missing, otherwise it will always return a non-empty
        list that begins with a lex token of ``open_kind`` and ends with a lex token of
        ``close_kind``. Advances the parser to the next lex token after the closing
        token.
        """
        if self.expect_optional_token(open_kind):
            nodes = [parse_fn()]
            append = nodes.append
            expect_optional_token = partial(self.expect_optional_token, close_kind)
            while not expect_optional_token():
                append(parse_fn())
            return nodes
        return []

    def many(
        self, open_kind: TokenKind, parse_fn: Callable[[], T], close_kind: TokenKind
    ) -> List[T]:
        """Fetch matching nodes, at least one.

        Returns a non-empty list of parse nodes, determined by the ``parse_fn``. This
        list begins with a lex token of ``open_kind`` and ends with a lex token of
        ``close_kind``. Advances the parser to the next lex token after the closing
        token.
        """
        self.expect_token(open_kind)
        nodes = [parse_fn()]
        append = nodes.append
        expect_optional_token = partial(self.expect_optional_token, close_kind)
        while not expect_optional_token():
            append(parse_fn())
        return nodes

    def delimited_many(
        self, delimiter_kind: TokenKind, parse_fn: Callable[[], T]
    ) -> List[T]:
        """Fetch many delimited nodes.

        Returns a non-empty list of parse nodes, determined by the ``parse_fn``. This
        list may begin with a lex token of ``delimiter_kind`` followed by items
        separated by lex tokens of ``delimiter_kind``. Advances the parser to the next
        lex token after the last item in the list.
        """
        expect_optional_token = partial(self.expect_optional_token, delimiter_kind)
        expect_optional_token()
        nodes: List[T] = []
        append = nodes.append
        while True:
            append(parse_fn())
            if not expect_optional_token():
                break
        return nodes

    def advance_lexer(self) -> None:
        max_tokens = self._max_tokens
        token = self._lexer.advance()

        if max_tokens is not None and token.kind != TokenKind.EOF:
            self._token_counter += 1
            if self._token_counter > max_tokens:
                raise GraphQLSyntaxError(
                    self._lexer.source,
                    token.start,
                    f"Document contains more than {max_tokens} tokens."
                    " Parsing aborted.",
                )


def get_token_desc(token: Token) -> str:
    """Describe a token as a string for debugging."""
    value = token.value
    return get_token_kind_desc(token.kind) + (
        f" '{value}'" if value is not None else ""
    )


def get_token_kind_desc(kind: TokenKind) -> str:
    """Describe a token kind as a string for debugging."""
    return f"'{kind.value}'" if is_punctuator_token_kind(kind) else kind.value
