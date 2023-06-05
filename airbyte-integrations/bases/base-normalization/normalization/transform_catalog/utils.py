#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Set, Union

from normalization.transform_catalog import dbt_macro


def jinja_call(command: Union[str, dbt_macro.Macro]) -> str:
    return "{{ " + command + " }}"


def remove_jinja(command: str) -> str:
    return str(command).replace("{{ ", "").replace(" }}", "")


def is_string(property_type) -> bool:
    return property_type == "string" or "string" in property_type


def is_datetime(definition: dict) -> bool:
    return (
        is_string(definition["type"])
        and ("format" in definition.keys())
        and (definition["format"] == "date-time" or "date-time" in definition["format"])
    )


def is_datetime_without_timezone(definition: dict) -> bool:
    return is_datetime(definition) and definition.get("airbyte_type") == "timestamp_without_timezone"


def is_datetime_with_timezone(definition: dict) -> bool:
    return is_datetime(definition) and (not definition.get("airbyte_type") or definition.get("airbyte_type") == "timestamp_with_timezone")


def is_date(definition: dict) -> bool:
    return (
        is_string(definition["type"])
        and ("format" in definition.keys())
        and (definition["format"] == "date" or "date" in definition["format"])
    )


def is_time(definition: dict) -> bool:
    return is_string(definition["type"]) and definition.get("format") == "time"


def is_time_with_timezone(definition: dict) -> bool:
    return is_time(definition) and definition.get("airbyte_type") == "time_with_timezone"


def is_time_without_timezone(definition: dict) -> bool:
    return is_time(definition) and definition.get("airbyte_type") == "time_without_timezone"


def is_number(property_type) -> bool:
    if is_string(property_type):
        # Handle union type, give priority to wider scope types
        return False
    return property_type == "number" or "number" in property_type


def is_big_integer(definition: dict) -> bool:
    return "airbyte_type" in definition and definition["airbyte_type"] == "big_integer"


def is_long(property_type, definition: dict) -> bool:
    # Check specifically for {type: number, airbyte_type: integer}
    if (
        (property_type == "number" or "number" in property_type)
        and "airbyte_type" in definition
        and definition["airbyte_type"] == "integer"
    ):
        return True
    if is_string(property_type) or is_number(property_type):
        # Handle union type, give priority to wider scope types
        return False
    return property_type == "integer" or "integer" in property_type


def is_boolean(property_type, definition: dict) -> bool:
    if is_string(property_type) or is_number(property_type) or is_big_integer(definition) or is_long(property_type, definition):
        # Handle union type, give priority to wider scope types
        return False
    return property_type == "boolean" or "boolean" in property_type


def is_array(property_type) -> bool:
    return property_type == "array" or "array" in property_type


def is_object(property_type) -> bool:
    return property_type == "object" or "object" in property_type


def is_airbyte_column(name: str) -> bool:
    return name.startswith("_airbyte_")


def is_simple_property(definition: dict) -> bool:
    if "type" not in definition:
        property_type = "object"
    else:
        property_type = definition["type"]
    return (
        is_string(property_type)
        or is_big_integer(definition)
        or is_long(property_type, definition)
        or is_number(property_type)
        or is_boolean(property_type, definition)
    )


def is_combining_node(properties: dict) -> Set[str]:
    return set(properties).intersection({"anyOf", "oneOf", "allOf"})
