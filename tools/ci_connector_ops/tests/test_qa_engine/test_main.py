#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pandas
from ci_connector_ops.qa_engine import main

def test_write_qa_report_to_gcs(tmp_path):
    output_path = tmp_path / "output.json"
    main.write_qa_report_to_gcs(main.DUMMY_REPORT, output_path)
    assert pandas.read_json(output_path).to_dict() == main.DUMMY_REPORT.to_dict()
