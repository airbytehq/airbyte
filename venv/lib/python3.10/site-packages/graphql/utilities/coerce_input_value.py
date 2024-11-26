from typing import Any, Callable, Dict, List, Optional, Union, cast


from ..error import GraphQLError
from ..pyutils import (
    Path,
    did_you_mean,
    inspect,
    is_iterable,
    print_path_list,
    suggestion_list,
    Undefined,
)
from ..type import (
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLList,
    GraphQLScalarType,
    is_leaf_type,
    is_input_object_type,
    is_list_type,
    is_non_null_type,
    GraphQLNonNull,
)

__all__ = ["coerce_input_value"]


OnErrorCB = Callable[[List[Union[str, int]], Any, GraphQLError], None]


def default_on_error(
    path: List[Union[str, int]], invalid_value: Any, error: GraphQLError
) -> None:
    error_prefix = "Invalid value " + inspect(invalid_value)
    if path:
        error_prefix += f" at 'value{print_path_list(path)}'"
    error.message = error_prefix + ": " + error.message
    raise error


def coerce_input_value(
    input_value: Any,
    type_: GraphQLInputType,
    on_error: OnErrorCB = default_on_error,
    path: Optional[Path] = None,
) -> Any:
    """Coerce a Python value given a GraphQL Input Type."""
    if is_non_null_type(type_):
        if input_value is not None and input_value is not Undefined:
            type_ = cast(GraphQLNonNull, type_)
            return coerce_input_value(input_value, type_.of_type, on_error, path)
        on_error(
            path.as_list() if path else [],
            input_value,
            GraphQLError(
                f"Expected non-nullable type '{inspect(type_)}' not to be None."
            ),
        )
        return Undefined

    if input_value is None or input_value is Undefined:
        # Explicitly return the value null.
        return None

    if is_list_type(type_):
        type_ = cast(GraphQLList, type_)
        item_type = type_.of_type
        if is_iterable(input_value):
            coerced_list: List[Any] = []
            append_item = coerced_list.append
            for index, item_value in enumerate(input_value):
                append_item(
                    coerce_input_value(
                        item_value, item_type, on_error, Path(path, index, None)
                    )
                )
            return coerced_list
        # Lists accept a non-list value as a list of one.
        return [coerce_input_value(input_value, item_type, on_error, path)]

    if is_input_object_type(type_):
        type_ = cast(GraphQLInputObjectType, type_)
        if not isinstance(input_value, dict):
            on_error(
                path.as_list() if path else [],
                input_value,
                GraphQLError(f"Expected type '{type_.name}' to be a mapping."),
            )
            return Undefined

        coerced_dict: Dict[str, Any] = {}
        fields = type_.fields

        for field_name, field in fields.items():
            field_value = input_value.get(field_name, Undefined)

            if field_value is Undefined:
                if field.default_value is not Undefined:
                    # Use out name as name if it exists (extension of GraphQL.js).
                    coerced_dict[field.out_name or field_name] = field.default_value
                elif is_non_null_type(field.type):  # pragma: no cover else
                    type_str = inspect(field.type)
                    on_error(
                        path.as_list() if path else [],
                        input_value,
                        GraphQLError(
                            f"Field '{field_name}' of required type '{type_str}'"
                            " was not provided."
                        ),
                    )
                continue

            coerced_dict[field.out_name or field_name] = coerce_input_value(
                field_value, field.type, on_error, Path(path, field_name, type_.name)
            )

        # Ensure every provided field is defined.
        for field_name in input_value:
            if field_name not in fields:
                suggestions = suggestion_list(field_name, fields)
                on_error(
                    path.as_list() if path else [],
                    input_value,
                    GraphQLError(
                        f"Field '{field_name}' is not defined by type '{type_.name}'."
                        + did_you_mean(suggestions)
                    ),
                )
        return type_.out_type(coerced_dict)

    if is_leaf_type(type_):
        # Scalars determine if a value is valid via `parse_value()`, which can throw to
        # indicate failure. If it throws, maintain a reference to the original error.
        type_ = cast(GraphQLScalarType, type_)
        try:
            parse_result = type_.parse_value(input_value)
        except GraphQLError as error:
            on_error(path.as_list() if path else [], input_value, error)
            return Undefined
        except Exception as error:
            on_error(
                path.as_list() if path else [],
                input_value,
                GraphQLError(
                    f"Expected type '{type_.name}'. {error}", original_error=error
                ),
            )
            return Undefined
        if parse_result is Undefined:
            on_error(
                path.as_list() if path else [],
                input_value,
                GraphQLError(f"Expected type '{type_.name}'."),
            )
        return parse_result

    # Not reachable. All possible input types have been considered.
    raise TypeError(f"Unexpected input type: {inspect(type_)}.")
