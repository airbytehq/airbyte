#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict


def transform_custom_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Method to detect custom fields that start with 'cf_' from chargbee models.
    Args:
        record:
        {
            ...
            'cf_custom_fields': 'some_value',
            ...
        }

    Returns:
        record:
        {
            ...
            'custom_fields': [{
                'name': 'cf_custom_fields',
                'value': some_value'
            }],
            ...
        }
    """
    custom_fields = []

    for key, value in record.items():
        if key.startswith("cf_"):
            custom_fields.append({"name": key, "value": value})

    record["custom_fields"] = custom_fields

    yield record
