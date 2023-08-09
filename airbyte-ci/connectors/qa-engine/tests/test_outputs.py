#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
import pytest
from qa_engine import outputs


@pytest.mark.parametrize("public_fields_only", [True, False])
def test_persist_qa_report(tmp_path, dummy_qa_report, public_fields_only):
    output_path = outputs.persist_qa_report(dummy_qa_report, str(tmp_path), public_fields_only=public_fields_only)
    qa_report_from_disk = pd.read_json(output_path, lines=True)
    private_fields = {field.name for field in outputs.ConnectorQAReport.__fields__.values() if not field.field_info.extra["is_public"]}
    available_fields = set(qa_report_from_disk.columns)
    if public_fields_only:
        assert not private_fields.issubset(available_fields)
    else:
        assert private_fields.issubset(available_fields)
