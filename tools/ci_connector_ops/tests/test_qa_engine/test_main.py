#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from ci_connector_ops.qa_engine import main
from click.testing import CliRunner


@pytest.mark.parametrize("create_prs", [False, True])
def test_main(mocker, dummy_qa_report, create_prs):
    runner = CliRunner()

    mock_oss_catalog = mocker.Mock(__len__=mocker.Mock(return_value=42))
    mock_cloud_catalog = mocker.Mock()

    mocker.patch.object(main, "enrichments")
    mocker.patch.object(main.inputs, "fetch_remote_catalog", mocker.Mock(side_effect=[mock_oss_catalog, mock_cloud_catalog]))
    mocker.patch.object(main.inputs, "fetch_adoption_metrics_per_connector_version")
    mocker.patch.object(main.validations, "get_qa_report", mocker.Mock(return_value=dummy_qa_report))
    mocker.patch.object(main.validations, "get_connectors_eligible_for_cloud")
    mocker.patch.object(main.cloud_availability_updater, "batch_deploy_eligible_connectors_to_cloud_repo")
    mocker.patch.object(main.outputs, "persist_qa_report")

    if create_prs:
        runner.invoke(main.main, ["--create-prs"])
    else:
        runner.invoke(main.main)

    assert main.inputs.fetch_remote_catalog.call_count == 2
    main.inputs.fetch_remote_catalog.assert_has_calls([mocker.call(main.OSS_CATALOG_URL), mocker.call(main.CLOUD_CATALOG_URL)])
    main.enrichments.get_enriched_catalog.assert_called_with(
        mock_oss_catalog, mock_cloud_catalog, main.inputs.fetch_adoption_metrics_per_connector_version.return_value
    )
    main.validations.get_qa_report.assert_called_with(main.enrichments.get_enriched_catalog.return_value, len(mock_oss_catalog))
    main.outputs.persist_qa_report.assert_called_with(
        main.validations.get_qa_report.return_value, main.GCS_QA_REPORT_PATH, public_fields_only=False
    )
    if create_prs:
        main.validations.get_connectors_eligible_for_cloud.assert_called_with(main.validations.get_qa_report.return_value)
        main.cloud_availability_updater.batch_deploy_eligible_connectors_to_cloud_repo.assert_called_with(
            main.validations.get_connectors_eligible_for_cloud.return_value
        )
