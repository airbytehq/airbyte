#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from typing import Set


def jinja_call(command: str) -> str:
    return "{{ " + command + " }}"


def is_string(property_type) -> bool:
    return property_type == "string" or "string" in property_type


def is_timestamp_with_time_zone(definition: dict) -> bool:
    return (
        is_string(definition["type"])
        and ("format" in definition.keys())
        and (definition["format"] == "date-time" or "date-time" in definition["format"])
    )


def is_date(definition: dict) -> bool:
    return (
        is_string(definition["type"])
        and ("format" in definition.keys())
        and (definition["format"] == "date" or "date" in definition["format"])
    )


def is_number(property_type) -> bool:
    if is_string(property_type):
        # Handle union type, give priority to wider scope types
        return False
    return property_type == "number" or "number" in property_type


def is_integer(property_type) -> bool:
    if is_string(property_type) or is_number(property_type):
        # Handle union type, give priority to wider scope types
        return False
    return property_type == "integer" or "integer" in property_type


def is_boolean(property_type) -> bool:
    if is_string(property_type) or is_number(property_type) or is_integer(property_type):
        # Handle union type, give priority to wider scope types
        return False
    return property_type == "boolean" or "boolean" in property_type


def is_array(property_type) -> bool:
    return property_type == "array" or "array" in property_type


def is_object(property_type) -> bool:
    return property_type == "object" or "object" in property_type


def is_airbyte_column(name: str) -> bool:
    return name.startswith("_airbyte_")


def is_simple_property(property_type) -> bool:
    return is_string(property_type) or is_integer(property_type) or is_number(property_type) or is_boolean(property_type)


def is_combining_node(properties: dict) -> Set[str]:
    return set(properties).intersection({"anyOf", "oneOf", "allOf"})
