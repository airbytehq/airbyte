from itertools import repeat

from graphql import DocumentNode, GraphQLSchema

from gql.dsl import DSLFragment, DSLMetaField, DSLQuery, DSLSchema, dsl_gql


def get_introspection_query_ast(
    descriptions: bool = True,
    specified_by_url: bool = False,
    directive_is_repeatable: bool = False,
    schema_description: bool = False,
    type_recursion_level: int = 7,
) -> DocumentNode:
    """Get a query for introspection as a document using the DSL module.

    Equivalent to the get_introspection_query function from graphql-core
    but using the DSL module and allowing to select the recursion level.

    Optionally, you can exclude descriptions, include specification URLs,
    include repeatability of directives, and specify whether to include
    the schema description as well.
    """

    ds = DSLSchema(GraphQLSchema())

    fragment_FullType = DSLFragment("FullType").on(ds.__Type)
    fragment_InputValue = DSLFragment("InputValue").on(ds.__InputValue)
    fragment_TypeRef = DSLFragment("TypeRef").on(ds.__Type)

    schema = DSLMetaField("__schema")

    if descriptions and schema_description:
        schema.select(ds.__Schema.description)

    schema.select(
        ds.__Schema.queryType.select(ds.__Type.name),
        ds.__Schema.mutationType.select(ds.__Type.name),
        ds.__Schema.subscriptionType.select(ds.__Type.name),
    )

    schema.select(ds.__Schema.types.select(fragment_FullType))

    directives = ds.__Schema.directives.select(ds.__Directive.name)

    if descriptions:
        directives.select(ds.__Directive.description)
    if directive_is_repeatable:
        directives.select(ds.__Directive.isRepeatable)
    directives.select(
        ds.__Directive.locations,
        ds.__Directive.args.select(fragment_InputValue),
    )

    schema.select(directives)

    fragment_FullType.select(
        ds.__Type.kind,
        ds.__Type.name,
    )
    if descriptions:
        fragment_FullType.select(ds.__Type.description)
    if specified_by_url:
        fragment_FullType.select(ds.__Type.specifiedByURL)

    fields = ds.__Type.fields(includeDeprecated=True).select(ds.__Field.name)

    if descriptions:
        fields.select(ds.__Field.description)

    fields.select(
        ds.__Field.args.select(fragment_InputValue),
        ds.__Field.type.select(fragment_TypeRef),
        ds.__Field.isDeprecated,
        ds.__Field.deprecationReason,
    )

    enum_values = ds.__Type.enumValues(includeDeprecated=True).select(
        ds.__EnumValue.name
    )

    if descriptions:
        enum_values.select(ds.__EnumValue.description)

    enum_values.select(
        ds.__EnumValue.isDeprecated,
        ds.__EnumValue.deprecationReason,
    )

    fragment_FullType.select(
        fields,
        ds.__Type.inputFields.select(fragment_InputValue),
        ds.__Type.interfaces.select(fragment_TypeRef),
        enum_values,
        ds.__Type.possibleTypes.select(fragment_TypeRef),
    )

    fragment_InputValue.select(ds.__InputValue.name)

    if descriptions:
        fragment_InputValue.select(ds.__InputValue.description)

    fragment_InputValue.select(
        ds.__InputValue.type.select(fragment_TypeRef),
        ds.__InputValue.defaultValue,
    )

    fragment_TypeRef.select(
        ds.__Type.kind,
        ds.__Type.name,
    )

    if type_recursion_level >= 1:
        current_field = ds.__Type.ofType.select(ds.__Type.kind, ds.__Type.name)
        fragment_TypeRef.select(current_field)

        for _ in repeat(None, type_recursion_level - 1):
            new_oftype = ds.__Type.ofType.select(ds.__Type.kind, ds.__Type.name)
            current_field.select(new_oftype)
            current_field = new_oftype

    query = DSLQuery(schema)

    query.name = "IntrospectionQuery"

    dsl_query = dsl_gql(query, fragment_FullType, fragment_InputValue, fragment_TypeRef)

    return dsl_query
