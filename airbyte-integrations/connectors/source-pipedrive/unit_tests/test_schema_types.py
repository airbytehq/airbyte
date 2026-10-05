# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Declared JSON types follow Pipedrive's API reference.

Values in the shape Pipedrive documents must validate against the declared stream schemas, otherwise
typed destinations drop them (lead ids are UUIDs; amounts can be fractional).
"""

from pathlib import Path

import jsonschema
import pytest
import yaml


_SCHEMAS = yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())["schemas"]
_LEAD_UUID = "adf21080-0e10-11eb-879b-05d71fb426ec"


@pytest.mark.parametrize(
    "stream, record",
    [
        pytest.param("notes", {"id": 1, "lead_id": _LEAD_UUID}, id="notes_lead_id_is_a_uuid"),
        pytest.param(
            "files",
            {"id": 1, "lead_id": _LEAD_UUID, "cid": "image001.png@01DB2F3A.4B5C6D70", "mail_message_id": "44", "mail_template_id": "7"},
            id="files_ids_are_strings",
        ),
        pytest.param("filters", {"id": 1, "temporary_flag": True}, id="filters_temporary_flag_is_boolean"),
        pytest.param("leads", {"id": _LEAD_UUID, "value": {"amount": 1234.56, "currency": "EUR"}}, id="leads_amount_can_be_fractional"),
        pytest.param(
            "mailThreads", {"id": 1, "version": 1.5, "parties": {"from": [{"message_time": 1712345678.25}]}}, id="mail_threads_numbers"
        ),
    ],
)
def test_vendor_shaped_values_validate_against_the_declared_schema(stream, record):
    jsonschema.validate(record, _SCHEMAS[stream])
