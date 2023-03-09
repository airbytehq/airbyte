#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
import pytest

from ci_connector_ops.qa_engine import main

@pytest.fixture
def dummy_report() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "connector_type": "source",
            "connector_name": "test",
            "docker_image_tag": "0.0.0",
            "release_stage": "alpha",
            "is_on_cloud": False,
            "latest_build_is_successful": False,
            "documentation_is_available": False,
            "number_of_connections": 0,
            "number_of_users": 0,
            "sync_success_rate": .99
        }
    ])

def test_main(tmp_path, mocker, dummy_report):
    output_path = tmp_path / "output.json"
    mocker.patch.object(main, "GCS_QA_REPORT_PATH", output_path)
    mocker.patch.object(main, "get_enriched_catalog")
    mocker.patch.object(main, "get_qa_report", mocker.Mock(return_value=dummy_report))
    main.main()
    main.get_enriched_catalog.assert_called_with(main.OSS_CATALOG, main.CLOUD_CATALOG)
    main.get_qa_report.assert_called_with(main.get_enriched_catalog.return_value)
    assert pd.read_json(output_path).to_dict() == dummy_report.to_dict()
