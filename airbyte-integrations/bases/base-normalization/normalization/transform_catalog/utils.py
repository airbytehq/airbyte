#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Callable, Set, Union

from normalization import data_type
from normalization.transform_catalog import dbt_macro


def jinja_call(command: Union[str, dbt_macro.Macro]) -> str:
    return "{{ " + command + " }}"


def remove_jinja(command: str) -> str:
    return str(command).replace("{{ ", "").replace(" }}", "")


def is_type_included(definition: dict, is_type: Callable[[dict], bool]) -> bool:
    if data_type.ONE_OF_VAR_NAME in definition:
        return bool(any(is_type_included(option, is_type) for option in definition[data_type.ONE_OF_VAR_NAME]))
    else:
        return is_type(definition)


def get_type_param(definition: dict, is_type: Callable[[dict], bool], param: str, default_value):
    # We're going to just pick the first oneOf entry. We don't handle conflicts yet.
    if data_type.ONE_OF_VAR_NAME in definition:
        for option in definition[data_type.ONE_OF_VAR_NAME]:
            # Recurse just in case this is yet another oneOf, for whatever reason
            return get_type_param(option, is_type, param, default_value)
    elif is_type(definition) and param in definition:
        # We're guaranteed that this isn't a oneOf, so this should be a raw array decl (or whatever)
        return definition[param]
    else:
        return default_value


def get_reftype_function(type: str) -> Callable[[dict], bool]:
    def is_reftype(definition: dict) -> bool:
        return data_type.REF_TYPE_VAR_NAME in definition and type == definition[data_type.REF_TYPE_VAR_NAME]

    return is_reftype


def is_string(definition: dict) -> bool:
    return is_type_included(definition, get_reftype_function(data_type.STRING_TYPE)) or is_type_included(
        definition, get_reftype_function(data_type.BINARY_DATA_TYPE)
    )


def is_binary_datatype(definition: dict) -> bool:
    return False
    # return is_type_included(definition, get_reftype_function(data_type.BINARY_DATA_TYPE))


def is_datetime(definition: dict) -> bool:
    return is_datetime_with_timezone(definition) or is_datetime_without_timezone(definition)


def is_datetime_without_timezone(definition: dict) -> bool:
    return is_type_included(definition, get_reftype_function(data_type.TIMESTAMP_WITHOUT_TIMEZONE_TYPE))


def is_datetime_with_timezone(definition: dict) -> bool:
    return is_type_included(definition, get_reftype_function(data_type.TIMESTAMP_WITH_TIMEZONE_TYPE))


def is_date(definition: dict) -> bool:
    return is_type_included(definition, get_reftype_function(data_type.DATE_TYPE))


def is_time(definition: dict) -> bool:
    return is_time_with_timezone(definition) or is_time_without_timezone(definition)


def is_time_with_timezone(definition: dict) -> bool:
    return is_type_included(definition, get_reftype_function(data_type.TIME_WITH_TIME_ZONE_TYPE))


def is_time_without_timezone(definition: dict) -> bool:
    return is_type_included(definition, get_reftype_function(data_type.TIME_WITHOUT_TIME_ZONE_TYPE))


def is_number(definition: dict) -> bool:
    if is_string(definition):
        # Handle union type, give priority to wider scope types
        return False
    return is_type_included(definition, get_reftype_function(data_type.NUMBER_TYPE))


# this is obsolete type that will not be used in new datatypes
def is_big_integer(definition: dict) -> bool:
    return False


def is_long(definition: dict) -> bool:
    return is_type_included(definition, get_reftype_function(data_type.INTEGER_TYPE))


def is_boolean(definition: dict) -> bool:
    if is_string(definition) or is_number(definition) or is_big_integer(definition) or is_long(definition):
        # Handle union type, give priority to wider scope types
        return False
    return is_type_included(definition, get_reftype_function(data_type.BOOLEAN_TYPE))


def is_array_schema(property_type) -> bool:
    return property_type == "array" or "array" in property_type


def is_array(definition: dict) -> bool:
    return is_type_included(
        definition, lambda schema: data_type.TYPE_VAR_NAME in schema and is_array_schema(schema[data_type.TYPE_VAR_NAME])
    )


def get_array_items(definition: dict, default_value):
    return get_type_param(
        definition,
        is_array,
        "items",
        default_value,
    )


def is_object_schema(property_type) -> bool:
    return property_type == "object" or "object" in property_type


def is_object(definition: dict) -> bool:
    return is_type_included(
        definition, lambda schema: data_type.TYPE_VAR_NAME in schema and is_object_schema(schema[data_type.TYPE_VAR_NAME])
    )


def is_typeless_schema(definition: dict) -> bool:
    return data_type.TYPE_VAR_NAME not in definition and data_type.REF_TYPE_VAR_NAME not in definition


def contains_typeless_schema(definition: dict) -> bool:
    return is_type_included(definition, is_typeless_schema)


def is_airbyte_column(name: str) -> bool:
    return name.startswith("_airbyte_")


def is_simple_property(definition: dict) -> bool:
    return (
        is_string(definition)
        or is_big_integer(definition)
        or is_long(definition)
        or is_number(definition)
        or is_boolean(definition)
        or is_date(definition)
        or is_time(definition)
        or is_datetime(definition)
        or is_binary_datatype(definition)
    )


def is_combining_node(properties: dict) -> Set[str]:
    # this case appears when we have analog of old protocol like id: {type:[number, string]} and it's handled separately
    if data_type.ONE_OF_VAR_NAME in properties and any(
        data_type.REF_TYPE_VAR_NAME in option and data_type.WELL_KNOWN_TYPE_VAR_NAME in option[data_type.REF_TYPE_VAR_NAME]
        for option in properties[data_type.ONE_OF_VAR_NAME]
    ):
        return set()
    else:
        return set(properties).intersection({"anyOf", "oneOf", "allOf"})
