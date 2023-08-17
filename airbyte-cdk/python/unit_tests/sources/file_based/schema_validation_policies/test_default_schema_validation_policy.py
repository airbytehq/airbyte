#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import ValidationPolicy
from airbyte_cdk.sources.file_based.exceptions import StopSyncPerValidationPolicy
from airbyte_cdk.sources.file_based.schema_validation_policies import DEFAULT_SCHEMA_VALIDATION_POLICIES

CONFORMING_RECORD = {
    "col1": "val1",
    "col2": 1,
}

NONCONFORMING_RECORD = {
    "col1": "val1",
    "extra_col": "x",
}


SCHEMA = {
    "type": "object",
    "properties": {
        "col1": {
            "type": "string"
        },
        "col2": {
            "type": "integer"
        },
    }
}


@pytest.mark.parametrize(
    "record,schema,validation_policy,expected_result",
    [
        pytest.param(CONFORMING_RECORD, SCHEMA, ValidationPolicy.emit_record, True, id="record-conforms_emit_record"),
        pytest.param(NONCONFORMING_RECORD, SCHEMA, ValidationPolicy.emit_record, True, id="nonconforming_emit_record"),
        pytest.param(CONFORMING_RECORD, SCHEMA, ValidationPolicy.skip_record, True, id="record-conforms_skip_record"),
        pytest.param(NONCONFORMING_RECORD, SCHEMA, ValidationPolicy.skip_record, False, id="nonconforming_skip_record"),
        pytest.param(CONFORMING_RECORD, SCHEMA, ValidationPolicy.wait_for_discover, True, id="record-conforms_wait_for_discover"),
        pytest.param(NONCONFORMING_RECORD, SCHEMA, ValidationPolicy.wait_for_discover, False, id="nonconforming_wait_for_discover"),
    ]
)
def test_record_passes_validation_policy(
    record: Mapping[str, Any],
    schema: Mapping[str, Any],
    validation_policy: ValidationPolicy,
    expected_result: bool
) -> None:
    if validation_policy == ValidationPolicy.wait_for_discover and expected_result is False:
        with pytest.raises(StopSyncPerValidationPolicy):
            DEFAULT_SCHEMA_VALIDATION_POLICIES[validation_policy].record_passes_validation_policy(record, schema)
    else:
        assert DEFAULT_SCHEMA_VALIDATION_POLICIES[validation_policy].record_passes_validation_policy(record, schema) == expected_result
