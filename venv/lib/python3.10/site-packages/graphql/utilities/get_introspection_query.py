from textwrap import dedent
from typing import Any, Dict, List, Optional, Union

from ..language import DirectiveLocation

try:
    from typing import TypedDict, Literal
except ImportError:  # Python < 3.8
    from typing_extensions import TypedDict, Literal  # type: ignore

__all__ = [
    "get_introspection_query",
    "IntrospectionDirective",
    "IntrospectionEnumType",
    "IntrospectionField",
    "IntrospectionInputObjectType",
    "IntrospectionInputValue",
    "IntrospectionInterfaceType",
    "IntrospectionListType",
    "IntrospectionNonNullType",
    "IntrospectionObjectType",
    "IntrospectionQuery",
    "IntrospectionScalarType",
    "IntrospectionSchema",
    "IntrospectionType",
    "IntrospectionTypeRef",
    "IntrospectionUnionType",
]


def get_introspection_query(
    descriptions: bool = True,
    specified_by_url: bool = False,
    directive_is_repeatable: bool = False,
    schema_description: bool = False,
    input_value_deprecation: bool = False,
) -> str:
    """Get a query for introspection.

    Optionally, you can exclude descriptions, include specification URLs,
    include repeatability of directives, and specify whether to include
    the schema description as well.
    """
    maybe_description = "description" if descriptions else ""
    maybe_specified_by_url = "specifiedByURL" if specified_by_url else ""
    maybe_directive_is_repeatable = "isRepeatable" if directive_is_repeatable else ""
    maybe_schema_description = maybe_description if schema_description else ""

    def input_deprecation(string: str) -> Optional[str]:
        return string if input_value_deprecation else ""

    return dedent(
        f"""
        query IntrospectionQuery {{
          __schema {{
            {maybe_schema_description}
            queryType {{ name }}
            mutationType {{ name }}
            subscriptionType {{ name }}
            types {{
              ...FullType
            }}
            directives {{
              name
              {maybe_description}
              {maybe_directive_is_repeatable}
              locations
              args{input_deprecation("(includeDeprecated: true)")} {{
                ...InputValue
              }}
            }}
          }}
        }}

        fragment FullType on __Type {{
          kind
          name
          {maybe_description}
          {maybe_specified_by_url}
          fields(includeDeprecated: true) {{
            name
            {maybe_description}
            args{input_deprecation("(includeDeprecated: true)")} {{
              ...InputValue
            }}
            type {{
              ...TypeRef
            }}
            isDeprecated
            deprecationReason
          }}
          inputFields{input_deprecation("(includeDeprecated: true)")} {{
            ...InputValue
          }}
          interfaces {{
            ...TypeRef
          }}
          enumValues(includeDeprecated: true) {{
            name
            {maybe_description}
            isDeprecated
            deprecationReason
          }}
          possibleTypes {{
            ...TypeRef
          }}
        }}

        fragment InputValue on __InputValue {{
          name
          {maybe_description}
          type {{ ...TypeRef }}
          defaultValue
          {input_deprecation("isDeprecated")}
          {input_deprecation("deprecationReason")}
        }}

        fragment TypeRef on __Type {{
          kind
          name
          ofType {{
            kind
            name
            ofType {{
              kind
              name
              ofType {{
                kind
                name
                ofType {{
                  kind
                  name
                  ofType {{
                    kind
                    name
                    ofType {{
                      kind
                      name
                      ofType {{
                        kind
                        name
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
    )


# Unfortunately, the following type definitions are a bit simplistic
# because of current restrictions in the typing system (mypy):
# - no recursion, see https://github.com/python/mypy/issues/731
# - no generic typed dicts, see https://github.com/python/mypy/issues/3863

# simplified IntrospectionNamedType to avoids cycles
SimpleIntrospectionType = Dict[str, Any]


class MaybeWithDescription(TypedDict, total=False):
    description: Optional[str]


class WithName(MaybeWithDescription):
    name: str


class MaybeWithSpecifiedByUrl(TypedDict, total=False):
    specifiedByURL: Optional[str]


class WithDeprecated(TypedDict):
    isDeprecated: bool
    deprecationReason: Optional[str]


class MaybeWithDeprecated(TypedDict, total=False):
    isDeprecated: bool
    deprecationReason: Optional[str]


class IntrospectionInputValue(WithName, MaybeWithDeprecated):
    type: SimpleIntrospectionType  # should be IntrospectionInputType
    defaultValue: Optional[str]


class IntrospectionField(WithName, WithDeprecated):
    args: List[IntrospectionInputValue]
    type: SimpleIntrospectionType  # should be IntrospectionOutputType


class IntrospectionEnumValue(WithName, WithDeprecated):
    pass


class MaybeWithIsRepeatable(TypedDict, total=False):
    isRepeatable: bool


class IntrospectionDirective(WithName, MaybeWithIsRepeatable):
    locations: List[DirectiveLocation]
    args: List[IntrospectionInputValue]


class IntrospectionScalarType(WithName, MaybeWithSpecifiedByUrl):
    kind: Literal["scalar"]


class IntrospectionInterfaceType(WithName):
    kind: Literal["interface"]
    fields: List[IntrospectionField]
    interfaces: List[SimpleIntrospectionType]  # should be InterfaceType
    possibleTypes: List[SimpleIntrospectionType]  # should be NamedType


class IntrospectionObjectType(WithName):
    kind: Literal["object"]
    fields: List[IntrospectionField]
    interfaces: List[SimpleIntrospectionType]  # should be InterfaceType


class IntrospectionUnionType(WithName):
    kind: Literal["union"]
    possibleTypes: List[SimpleIntrospectionType]  # should be NamedType


class IntrospectionEnumType(WithName):
    kind: Literal["enum"]
    enumValues: List[IntrospectionEnumValue]


class IntrospectionInputObjectType(WithName):
    kind: Literal["input_object"]
    inputFields: List[IntrospectionInputValue]


IntrospectionType = Union[
    IntrospectionScalarType,
    IntrospectionObjectType,
    IntrospectionInterfaceType,
    IntrospectionUnionType,
    IntrospectionEnumType,
    IntrospectionInputObjectType,
]


IntrospectionOutputType = Union[
    IntrospectionScalarType,
    IntrospectionObjectType,
    IntrospectionInterfaceType,
    IntrospectionUnionType,
    IntrospectionEnumType,
]


IntrospectionInputType = Union[
    IntrospectionScalarType, IntrospectionEnumType, IntrospectionInputObjectType
]


class IntrospectionListType(TypedDict):
    kind: Literal["list"]
    ofType: SimpleIntrospectionType  # should be IntrospectionType


class IntrospectionNonNullType(TypedDict):
    kind: Literal["non_null"]
    ofType: SimpleIntrospectionType  # should be IntrospectionType


IntrospectionTypeRef = Union[
    IntrospectionType, IntrospectionListType, IntrospectionNonNullType
]


class IntrospectionSchema(MaybeWithDescription):
    queryType: IntrospectionObjectType
    mutationType: Optional[IntrospectionObjectType]
    subscriptionType: Optional[IntrospectionObjectType]
    types: List[IntrospectionType]
    directives: List[IntrospectionDirective]


class IntrospectionQuery(TypedDict):
    """The root typed dictionary for schema introspections."""

    __schema: IntrospectionSchema
