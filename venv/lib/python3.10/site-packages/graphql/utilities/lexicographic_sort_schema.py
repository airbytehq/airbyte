from typing import Collection, Dict, Optional, Tuple, Union, cast

from ..language import DirectiveLocation
from ..pyutils import inspect, merge_kwargs, natural_comparison_key
from ..type import (
    GraphQLArgument,
    GraphQLDirective,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNamedType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLUnionType,
    is_enum_type,
    is_input_object_type,
    is_interface_type,
    is_introspection_type,
    is_list_type,
    is_non_null_type,
    is_object_type,
    is_scalar_type,
    is_union_type,
)

__all__ = ["lexicographic_sort_schema"]


def lexicographic_sort_schema(schema: GraphQLSchema) -> GraphQLSchema:
    """Sort GraphQLSchema.

    This function returns a sorted copy of the given GraphQLSchema.
    """

    def replace_type(
        type_: Union[GraphQLList, GraphQLNonNull, GraphQLNamedType]
    ) -> Union[GraphQLList, GraphQLNonNull, GraphQLNamedType]:
        if is_list_type(type_):
            return GraphQLList(replace_type(cast(GraphQLList, type_).of_type))
        if is_non_null_type(type_):
            return GraphQLNonNull(replace_type(cast(GraphQLNonNull, type_).of_type))
        return replace_named_type(cast(GraphQLNamedType, type_))

    def replace_named_type(type_: GraphQLNamedType) -> GraphQLNamedType:
        return type_map[type_.name]

    def replace_maybe_type(
        maybe_type: Optional[GraphQLNamedType],
    ) -> Optional[GraphQLNamedType]:
        return maybe_type and replace_named_type(maybe_type)

    def sort_directive(directive: GraphQLDirective) -> GraphQLDirective:
        return GraphQLDirective(
            **merge_kwargs(
                directive.to_kwargs(),
                locations=sorted(directive.locations, key=sort_by_name_key),
                args=sort_args(directive.args),
            )
        )

    def sort_args(args_map: Dict[str, GraphQLArgument]) -> Dict[str, GraphQLArgument]:
        args = {}
        for name, arg in sorted(args_map.items()):
            args[name] = GraphQLArgument(
                **merge_kwargs(
                    arg.to_kwargs(),
                    type_=replace_type(cast(GraphQLNamedType, arg.type)),
                )
            )
        return args

    def sort_fields(fields_map: Dict[str, GraphQLField]) -> Dict[str, GraphQLField]:
        fields = {}
        for name, field in sorted(fields_map.items()):
            fields[name] = GraphQLField(
                **merge_kwargs(
                    field.to_kwargs(),
                    type_=replace_type(cast(GraphQLNamedType, field.type)),
                    args=sort_args(field.args),
                )
            )
        return fields

    def sort_input_fields(
        fields_map: Dict[str, GraphQLInputField]
    ) -> Dict[str, GraphQLInputField]:
        return {
            name: GraphQLInputField(
                cast(
                    GraphQLInputType, replace_type(cast(GraphQLNamedType, field.type))
                ),
                description=field.description,
                default_value=field.default_value,
                ast_node=field.ast_node,
            )
            for name, field in sorted(fields_map.items())
        }

    def sort_types(array: Collection[GraphQLNamedType]) -> Tuple[GraphQLNamedType, ...]:
        return tuple(
            replace_named_type(type_) for type_ in sorted(array, key=sort_by_name_key)
        )

    def sort_named_type(type_: GraphQLNamedType) -> GraphQLNamedType:
        if is_scalar_type(type_) or is_introspection_type(type_):
            return type_
        if is_object_type(type_):
            type_ = cast(GraphQLObjectType, type_)
            return GraphQLObjectType(
                **merge_kwargs(
                    type_.to_kwargs(),
                    interfaces=lambda: sort_types(type_.interfaces),
                    fields=lambda: sort_fields(type_.fields),
                )
            )
        if is_interface_type(type_):
            type_ = cast(GraphQLInterfaceType, type_)
            return GraphQLInterfaceType(
                **merge_kwargs(
                    type_.to_kwargs(),
                    interfaces=lambda: sort_types(type_.interfaces),
                    fields=lambda: sort_fields(type_.fields),
                )
            )
        if is_union_type(type_):
            type_ = cast(GraphQLUnionType, type_)
            return GraphQLUnionType(
                **merge_kwargs(type_.to_kwargs(), types=lambda: sort_types(type_.types))
            )
        if is_enum_type(type_):
            type_ = cast(GraphQLEnumType, type_)
            return GraphQLEnumType(
                **merge_kwargs(
                    type_.to_kwargs(),
                    values={
                        name: GraphQLEnumValue(
                            val.value,
                            description=val.description,
                            deprecation_reason=val.deprecation_reason,
                            ast_node=val.ast_node,
                        )
                        for name, val in sorted(type_.values.items())
                    },
                )
            )
        if is_input_object_type(type_):
            type_ = cast(GraphQLInputObjectType, type_)
            return GraphQLInputObjectType(
                **merge_kwargs(
                    type_.to_kwargs(),
                    fields=lambda: sort_input_fields(type_.fields),
                )
            )

        # Not reachable. All possible types have been considered.
        raise TypeError(f"Unexpected type: {inspect(type_)}.")

    type_map: Dict[str, GraphQLNamedType] = {
        type_.name: sort_named_type(type_)
        for type_ in sorted(schema.type_map.values(), key=sort_by_name_key)
    }

    return GraphQLSchema(
        types=type_map.values(),
        directives=[
            sort_directive(directive)
            for directive in sorted(schema.directives, key=sort_by_name_key)
        ],
        query=cast(Optional[GraphQLObjectType], replace_maybe_type(schema.query_type)),
        mutation=cast(
            Optional[GraphQLObjectType], replace_maybe_type(schema.mutation_type)
        ),
        subscription=cast(
            Optional[GraphQLObjectType], replace_maybe_type(schema.subscription_type)
        ),
        ast_node=schema.ast_node,
    )


def sort_by_name_key(
    type_: Union[GraphQLNamedType, GraphQLDirective, DirectiveLocation]
) -> Tuple:
    return natural_comparison_key(type_.name)
