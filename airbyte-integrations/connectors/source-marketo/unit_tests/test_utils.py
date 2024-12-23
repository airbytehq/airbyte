#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime

import pytest
from source_marketo.utils import clean_string, format_value, to_datetime_str


test_data = [
    (1, {"type": "integer"}, int),
    ("string", {"type": "string"}, str),
    (True, {"type": ["boolean", "null"]}, bool),
    (1, {"type": ["number", "null"]}, float),
    ("", {"type": ["number", "null"]}, type(None)),
    ("1.5", {"type": "integer"}, int),
    ("15", {"type": "integer"}, int),
    ("true", {"type": "boolean"}, bool),
    ("test_custom", {"type": "custom_type"}, str),
]


@pytest.mark.parametrize("value,schema,expected_output_type", test_data)
def test_format_value(value, schema, expected_output_type):
    test = format_value(value, schema)

    assert isinstance(test, expected_output_type)


test_data = [
    ("api method name", "api_method_name"),
    ("API Method Name", "api_method_name"),
    ("modifying user", "modifying_user"),
    ("Modifying User", "modifying_user"),
    ("request id", "request_id"),
    ("Request Id", "request_id"),
    ("Page URL", "page_url"),
    ("Client IP Address", "client_ip_address"),
    ("Marketo Sales Person ID", "marketo_sales_person_id"),
    ("Merge IDs", "merge_ids"),
    ("SFDC Type", "sfdc_type"),
    ("Remove from CRM", "remove_from_crm"),
    ("SLA Expiration", "sla_expiration"),
    ("updatedAt", "updated_at"),
    ("UpdatedAt", "updated_at"),
    ("base URL", "base_url"),
    ("UPdatedAt", "u_pdated_at"),
    ("updated_at", "updated_at"),
    (" updated_at ", "updated_at"),
    ("updatedat", "updatedat"),
    ("", ""),
]


@pytest.mark.parametrize("value,expected", test_data)
def test_clean_string(value, expected):
    test = clean_string(value)

    assert test == expected


def test_to_datetime_str():
    input_ = datetime(2023, 1, 1)
    expected = "2023-01-01T00:00:00Z"

    assert to_datetime_str(input_) == expected
