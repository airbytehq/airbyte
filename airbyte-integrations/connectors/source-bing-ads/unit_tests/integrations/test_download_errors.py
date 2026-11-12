# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http.response_builder import find_template


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "budget_summary_report", "my_custom_report", "MyCustomReport"])
@pytest.mark.parametrize(
    "error_code,detail,expected_failure",
    [
        ("AuthenticationFailed", "Signature not valid in the specified time frame.", FailureType.transient_error),
        ("AuthenticationFailed", "Signature did not match.", FailureType.config_error),
        ("AuthorizationPermissionMismatch", "This request is not authorized to perform this operation.", FailureType.config_error),
    ],
)
def test_download_failure_classification(requests_mock, stream_name, error_code, detail, expected_failure):
    config = ConfigBuilder().with_reports_start_date("2024-01-01").build()
    if stream_name in ("my_custom_report", "MyCustomReport"):
        config["custom_reports"] = [
            {
                "name": "MyCustomReport",
                "reporting_object": "AgeGenderAudienceReportRequest",
                "report_columns": ["AccountId", "TimePeriod"],
                "report_aggregation": "Daily",
                "disable_custom_report_names_camel_to_snake_conversion": stream_name == "MyCustomReport",
            }
        ]
    requests_mock.post(
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        json=find_template("oauth", __file__),
    )
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/User/Query",
        json=find_template("user_query", __file__),
    )
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json=find_template("accounts_search_for_report", __file__),
    )
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/report.csv?sig=test"
    if stream_name == "app_install_ads":
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json=find_template("bulk_download", __file__),
        )
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
            json={"RequestStatus": "Completed", "ResultFileUrl": download_url},
        )
    else:
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json=find_template("generate_report", __file__),
        )
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": download_url}},
        )
    body = (
        '<?xml version="1.0" encoding="utf-8"?>'
        f"<Error><Code>{error_code}</Code><Message>Server failed to authenticate the request.</Message>"
        f"<AuthenticationErrorDetail>{detail}</AuthenticationErrorDetail></Error>"
    )
    download = requests_mock.get(download_url, status_code=403, text=body, headers={"Content-Type": "application/xml"})

    output = read_helper(
        config,
        CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build(),
        expecting_exception=True,
    )

    assert output.records == []
    error = output.errors[0].trace.error
    assert error.failure_type == expected_failure
    if expected_failure == FailureType.transient_error:
        assert error.message == f"Bing Ads download link for stream '{stream_name}' is outside its validity period."
    else:
        assert error.message == "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."
    assert detail in error.internal_message
    assert download.call_count == 1
