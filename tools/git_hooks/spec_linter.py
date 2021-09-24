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
"""
This script is responsible for connectors spec.json file validation.

Input:
List of spec files

Output:
exit code 0 - check is success
exit code 1 - check failed for at least one spec file

How spec file validation works:
1. read spec file and serialize it as python dict object
2. get properties field from spec object
3. check if all fields from FIELDS_TO_CHECK exist in each property
4. if field has oneOf attribute - fetch all subobjects and for each of them goto step (2)
"""

import json
import logging
import sys
from typing import Any, List, Mapping, Optional

# required fields for each property field in spec
FIELDS_TO_CHECK = {"title", "description"}
# configure logging
logging.basicConfig(format="%(message)s")


def read_spec_file(spec_path: str) -> bool:
    errors: List[str] = []
    with open(spec_path) as json_file:
        try:
            root_schema = json.load(json_file)["connectionSpecification"]["properties"]
        except (KeyError, TypeError):
            errors.append("Couldn't find properties in connector spec.json")
        except json.JSONDecodeError:
            errors.append("Couldn't parse json file")
        else:
            errors.extend(validate_schema(spec_path, root_schema))

    for msg in errors:
        logging.error(f"\033[1m{spec_path}\033[0m:{msg}")

    return False if errors else True


def validate_schema(
    spec_path: str,
    schema: Mapping[str, Any],
    parent_fields: Optional[List[str]] = None,
) -> List[str]:
    errors: List[str] = []
    parent_fields = parent_fields if parent_fields else []
    for field_name, field_schema in schema.items():
        errors.extend(validate_field(field_name, field_schema, parent_fields))
        if errors:
            continue

        for index, oneof_schema in enumerate(fetch_oneof_schemas(field_schema)):
            errors.extend(
                validate_schema(
                    spec_path,
                    oneof_schema["properties"],
                    parent_fields + [field_name, str(index)],
                )
            )

    return errors


def fetch_oneof_schemas(schema: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    """
    Finds subschemas in oneOf field
    """
    return [spec for spec in schema.get("oneOf", []) if spec.get("properties")]


def validate_field(
    field_name: str,
    schema: Mapping[str, Any],
    parent_fields: Optional[List[str]] = None,
) -> List[str]:
    """
    Validates single field objects and return errors if thay are exist
    """
    errors: List[str] = []
    full_field_name = get_full_field_name(field_name, parent_fields)

    if not FIELDS_TO_CHECK.issubset(schema.keys()):
        errors.append("Check failed for field")

    if schema.get("oneOf") and (schema["type"] != "object" or not isinstance(schema["oneOf"], list)):
        errors.append("Incorrect oneOf schema in field")

    return [f"{e} \x1b[31;1m{full_field_name}\033[0m" for e in errors]


def get_full_field_name(field_name: str, parent_fields: Optional[List[str]] = None) -> str:
    """
    Returns full path to a field.
    e.g. root.middle.child, root.oneof.1.attr
    """
    return ".".join(parent_fields + [field_name]) if parent_fields else field_name


if __name__ == "__main__":
    spec_files = sys.argv[1:]

    if not all([read_spec_file(file_path) for file_path in spec_files]):
        exit(1)
