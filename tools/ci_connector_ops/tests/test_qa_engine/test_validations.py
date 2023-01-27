#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
import pytest

from ci_connector_ops.qa_engine import enrichments, inputs, models, validations

@pytest.fixture
def enriched_catalog() -> pd.DataFrame:
    return enrichments.get_enriched_catalog(inputs.OSS_CATALOG, inputs.CLOUD_CATALOG)

@pytest.fixture
def qa_report(enriched_catalog, mocker) -> pd.DataFrame:
    mocker.patch.object(validations, "url_is_reachable", mocker.Mock(return_value=True))
    return validations.get_qa_report(enriched_catalog)

@pytest.fixture
def qa_report_columns(qa_report: pd.DataFrame) -> set:
    return set(qa_report.columns)

def test_all_columns_are_declared(qa_report_columns: set):
    expected_columns = set([field.name for field in models.ConnectorQAReport.__fields__.values()])
    assert qa_report_columns == expected_columns

def test_not_null_values_after_validation(qa_report: pd.DataFrame):
    assert len(qa_report.dropna()) == len(qa_report)

def test_report_generation_error(enriched_catalog, mocker):
    mocker.patch.object(validations, "url_is_reachable", mocker.Mock(return_value=True))
    with pytest.raises(validations.QAReportGenerationError):
        return validations.get_qa_report(enriched_catalog.sample(10))

@pytest.mark.parametrize(
    "connector_qa_data, expected_to_be_eligible",
    [
        (
            pd.Series({
                "is_on_cloud": False,
                "documentation_is_available": True,
                "is_appropriate_for_cloud_use": True,
                "latest_build_is_successful": True
            }),
            True
        ),
        (
            pd.Series({
                "is_on_cloud": True,
                "documentation_is_available": True,
                "is_appropriate_for_cloud_use": True,
                "latest_build_is_successful": True
            }),
            False
        ),
        (
            pd.Series({
                "is_on_cloud": True,
                "documentation_is_available": False,
                "is_appropriate_for_cloud_use": False,
                "latest_build_is_successful": False
            }),
            False
        ),
        (
            pd.Series({
                "is_on_cloud": False,
                "documentation_is_available": False,
                "is_appropriate_for_cloud_use": True,
                "latest_build_is_successful": True
            }),
            False
        ),
        (
            pd.Series({
                "is_on_cloud": False,
                "documentation_is_available": True,
                "is_appropriate_for_cloud_use": False,
                "latest_build_is_successful": True
            }),
            False
        ),
        (
            pd.Series({
                "is_on_cloud": False,
                "documentation_is_available": True,
                "is_appropriate_for_cloud_use": True,
                "latest_build_is_successful": False
            }),
            False
        )
    ]
)
def test_is_eligible_for_promotion_to_cloud(connector_qa_data: pd.Series, expected_to_be_eligible: bool):
    assert validations.is_eligible_for_promotion_to_cloud(connector_qa_data) == expected_to_be_eligible

def test_get_connectors_eligible_for_cloud(qa_report: pd.DataFrame):
    qa_report["is_eligible_for_promotion_to_cloud"] = True
    connectors_eligible_for_cloud = list(validations.get_connectors_eligible_for_cloud(qa_report))
    assert len(qa_report) == len(connectors_eligible_for_cloud)
    assert all([c.is_eligible_for_promotion_to_cloud for c in connectors_eligible_for_cloud])

    qa_report["is_eligible_for_promotion_to_cloud"] = False
    connectors_eligible_for_cloud = list(validations.get_connectors_eligible_for_cloud(qa_report))
    assert len(connectors_eligible_for_cloud) == 0
