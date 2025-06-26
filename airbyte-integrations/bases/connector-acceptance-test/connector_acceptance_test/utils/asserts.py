#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import logging
import re
from collections import defaultdict
from typing import Any, Dict, List, Mapping

import pendulum
from jsonschema import Draft7Validator, FormatChecker, FormatError, ValidationError, validators

from airbyte_protocol.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog


# fmt: off
timestamp_regex = re.compile((r"^\d{4}-\d?\d-\d?\d"  # date
                              r"(\s|T)"  # separator
                              r"\d?\d:\d?\d:\d?\d(.\d+)?"  # time
                              r".*$"))  # timezone
# fmt: on

# In Json schema, numbers with a zero fractional part are considered integers. E.G. 1.0 is considered a valid integer
# For stricter type validation we don't want to keep this behavior. We want to consider integers in the Pythonic way.
strict_integer_type_checker = Draft7Validator.TYPE_CHECKER.redefine("integer", lambda _, value: isinstance(value, int))
Draft7ValidatorWithStrictInteger = validators.extend(Draft7Validator, type_checker=strict_integer_type_checker)


class NoAdditionalPropertiesValidator(Draft7Validator):
    def __init__(self, schema, **kwargs):
        schema = self._enforce_false_additional_properties(schema)
        super().__init__(schema, **kwargs)

    @staticmethod
    def _enforce_false_additional_properties(json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create a copy of the schema in which `additionalProperties` is set to False for all non-null object properties.

        This method will override the value of `additionalProperties` if it is set,
        or will create the property and set it to False if it does not exist.
        """
        new_schema = copy.deepcopy(json_schema)
        new_schema["additionalProperties"] = False

        def add_properties(properties):
            for prop_name, prop_value in properties.items():
                if "type" in prop_value and "object" in prop_value["type"] and len(prop_value.get("properties", [])):
                    prop_value["additionalProperties"] = False
                    add_properties(prop_value.get("properties", {}))
                elif "type" in prop_value and "array" in prop_value["type"]:
                    if (
                        prop_value.get("items")
                        and "object" in prop_value.get("items", {}).get("type", [])
                        and len(prop_value.get("items", {}).get("properties", []))
                    ):
                        prop_value["items"]["additionalProperties"] = False
                    if prop_value.get("items", {}).get("properties"):
                        add_properties(prop_value["items"]["properties"])

        add_properties(new_schema.get("properties", {}))
        return new_schema


class CustomFormatChecker(FormatChecker):
    @staticmethod
    def check_datetime(value: str) -> bool:
        valid_format = timestamp_regex.match(value)
        try:
            pendulum.parse(value, strict=False)
        except ValueError:
            valid_time = False
        else:
            valid_time = True
        return valid_format and valid_time

    def check(self, instance, format):
        if instance is not None and format == "date-time":
            if not self.check_datetime(instance):
                raise FormatError(f"{instance} has invalid datetime format")
        else:
            return super().check(instance, format)


def verify_records_schema(
    records: List[AirbyteRecordMessage], catalog: ConfiguredAirbyteCatalog
) -> Mapping[str, Mapping[str, ValidationError]]:
    """Check records against their schemas from the catalog, yield error messages.
    Only first record with error will be yielded for each stream.
    """
    stream_validators = {}
    for stream in catalog.streams:
        schema_to_validate_against = stream.stream.json_schema
        # We will be disabling strict `NoAdditionalPropertiesValidator` until we have a better plan for schema validation. The consequence
        # is that we will lack visibility on new fields that are not added on the root level (root level is validated by Datadog)
        #   validator = NoAdditionalPropertiesValidator if fail_on_extra_columns else Draft7ValidatorWithStrictInteger
        validator = Draft7ValidatorWithStrictInteger
        stream_validators[stream.stream.name] = validator(schema_to_validate_against, format_checker=CustomFormatChecker())
    stream_errors = defaultdict(dict)
    for record in records:
        validator = stream_validators.get(record.stream)
        if not validator:
            logging.error(f"Received record from the `{record.stream}` stream, which is not in the catalog.")
            continue

        errors = list(validator.iter_errors(record.data))
        for error in errors:
            stream_errors[record.stream][str(error.schema_path)] = error

    return stream_errors
