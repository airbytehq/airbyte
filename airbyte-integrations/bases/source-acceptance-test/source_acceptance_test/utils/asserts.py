#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import re
from collections import defaultdict
from typing import List, Mapping

import pendulum
from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog
from jsonschema import Draft7Validator, FormatChecker, FormatError, ValidationError

# fmt: off
timestamp_regex = re.compile((r"^\d{4}-\d?\d-\d?\d"  # date
                              r"(\s|T)"  # separator
                              r"\d?\d:\d?\d:\d?\d(.\d+)?"  # time
                              r".*$"))  # timezone
# fmt: on


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
    validators = {}
    for stream in catalog.streams:
        validators[stream.stream.name] = Draft7Validator(stream.stream.json_schema, format_checker=CustomFormatChecker())

    stream_errors = defaultdict(dict)

    for record in records:
        validator = validators.get(record.stream)
        if not validator:
            logging.error(f"Record from the {record.stream} stream that is not in the catalog.")
            continue

        errors = list(validator.iter_errors(record.data))
        for error in errors:
            stream_errors[record.stream][str(error.schema_path)] = error

    return stream_errors
