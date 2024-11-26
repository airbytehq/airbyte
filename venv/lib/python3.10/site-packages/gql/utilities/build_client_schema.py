from graphql import GraphQLSchema, IntrospectionQuery
from graphql import build_client_schema as build_client_schema_orig
from graphql.pyutils import inspect
from graphql.utilities.get_introspection_query import (
    DirectiveLocation,
    IntrospectionDirective,
)

__all__ = ["build_client_schema"]


INCLUDE_DIRECTIVE_JSON: IntrospectionDirective = {
    "name": "include",
    "description": (
        "Directs the executor to include this field or fragment "
        "only when the `if` argument is true."
    ),
    "locations": [
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    "args": [
        {
            "name": "if",
            "description": "Included when true.",
            "type": {
                "kind": "NON_NULL",
                "name": "None",
                "ofType": {"kind": "SCALAR", "name": "Boolean", "ofType": "None"},
            },
            "defaultValue": "None",
        }
    ],
}

SKIP_DIRECTIVE_JSON: IntrospectionDirective = {
    "name": "skip",
    "description": (
        "Directs the executor to skip this field or fragment "
        "when the `if` argument is true."
    ),
    "locations": [
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    "args": [
        {
            "name": "if",
            "description": "Skipped when true.",
            "type": {
                "kind": "NON_NULL",
                "name": "None",
                "ofType": {"kind": "SCALAR", "name": "Boolean", "ofType": "None"},
            },
            "defaultValue": "None",
        }
    ],
}


def build_client_schema(introspection: IntrospectionQuery) -> GraphQLSchema:
    """This is an alternative to the graphql-core function
    :code:`build_client_schema` but with default include and skip directives
    added to the schema to fix
    `issue #278 <https://github.com/graphql-python/gql/issues/278>`_

    .. warning::
        This function will be removed once the issue
        `graphql-js#3419 <https://github.com/graphql/graphql-js/issues/3419>`_
        has been fixed and ported to graphql-core so don't use it
        outside gql.
    """

    if not isinstance(introspection, dict) or not isinstance(
        introspection.get("__schema"), dict
    ):
        raise TypeError(
            "Invalid or incomplete introspection result. Ensure that you"
            " are passing the 'data' attribute of an introspection response"
            f" and no 'errors' were returned alongside: {inspect(introspection)}."
        )

    schema_introspection = introspection["__schema"]

    directives = schema_introspection.get("directives", None)

    if directives is None:
        schema_introspection["directives"] = directives = []

    if not any(directive["name"] == "skip" for directive in directives):
        directives.append(SKIP_DIRECTIVE_JSON)

    if not any(directive["name"] == "include" for directive in directives):
        directives.append(INCLUDE_DIRECTIVE_JSON)

    return build_client_schema_orig(introspection, assume_valid=False)
