#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
import pytest

from ci_connector_ops.qa_engine import inputs, enrichments, models, validations

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
