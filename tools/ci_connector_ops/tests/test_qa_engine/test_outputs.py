#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
import pytest

from ci_connector_ops.qa_engine import outputs

@pytest.mark.parametrize("public_fields_only", [True, False])
def test_persist_qa_report_public_fields_only(tmp_path, dummy_qa_report, public_fields_only):
    output_path = tmp_path / "qa_report.json"
    outputs.persist_qa_report(dummy_qa_report, output_path, public_fields_only=public_fields_only)
    qa_report_from_disk = pd.read_json(output_path)
    private_fields = {
        field.name for field in outputs.ConnectorQAReport.__fields__.values() 
        if not field.field_info.extra["is_public"]
    }
    available_fields = set(qa_report_from_disk.columns)
    if public_fields_only:
        assert not private_fields.issubset(available_fields)
    else:
        assert private_fields.issubset(available_fields)
