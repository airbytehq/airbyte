#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from components import ReportPollingRequester


@pytest.mark.parametrize(
    ("reason", "is_missing"),
    [
        # Amazon's verbatim wording, captured from a canary against a live Vendor connection and also
        # reported in amzn/selling-partner-api-models#398.
        pytest.param(
            "Error in report request: This report type requires the reportPeriod, distributorView, "
            "sellingProgram reportOption to be specified. Please review the document for this report type "
            "on GitHub, provide a value for this reportOption in your request, and try again.",
            True,
            id="amazon_requires_to_be_specified",
        ),
        # Illustrative wordings below: not captured from Amazon.
        pytest.param("Error in report request: a required reportOption is missing.", True, id="required_is_missing"),
        pytest.param("Missing required option: reportPeriod.", True, id="missing_required_option"),
        pytest.param("reportPeriod must be specified.", True, id="must_be_specified"),
        # The option was sent and Amazon rejected its value: the user already set it.
        pytest.param("Invalid reportPeriod WEEK: dataStartTime must fall on a Sunday.", False, id="misaligned_week"),
        # Guards against a bare "requires" marker, which would misclassify this one.
        pytest.param("reportPeriod WEEK requires dataStartTime to be a Sunday.", False, id="misaligned_week_requires"),
        pytest.param("MANUFACTURING is not a valid distributorView for this vendor group.", False, id="invalid_distributor_view"),
    ],
)
def test_is_missing_report_option_error(reason: str, is_missing: bool) -> None:
    assert ReportPollingRequester._is_missing_report_option_error(reason) is is_missing


# Amazon's verbatim FATAL reasons that are not report-options problems. They must fall through to
# the existing retry path rather than raise a config error.
@pytest.mark.parametrize(
    "reason",
    [
        # Captured from the #85294 canary.
        pytest.param("The report data for the requested date range is not yet available", id="not_yet_available"),
        # Captured from the #85294 canary, also in amzn/selling-partner-api-models discussion #3785.
        pytest.param("dataStartTime and dataEndTime must be supplied", id="no_date_window"),
        # amzn/selling-partner-api-models#4701, from a weekly report request.
        pytest.param(
            "A client error occurred. Please double check that your parameters are valid and fulfill the requirements of the report type.",
            id="generic_client_error",
        ),
    ],
)
def test_given_unrelated_amazon_reason_then_not_a_report_options_error(reason: str) -> None:
    assert ReportPollingRequester._is_report_options_error(reason) is False
    assert ReportPollingRequester._is_missing_report_option_error(reason) is False


def test_given_value_error_when_building_message_then_no_add_advice() -> None:
    reason = "Invalid reportPeriod WEEK: dataStartTime must fall on a Sunday."

    message = ReportPollingRequester._report_options_error_message("GET_VENDOR_SALES_REPORT", reason)

    assert f'Amazon\'s reason: "{reason}"' in message
    assert "Check the values set for GET_VENDOR_SALES_REPORT under Report Options" in message
    assert "Add the options under Report Options" not in message
    assert "Amazon documents" not in message


def test_given_missing_option_when_building_message_then_add_advice() -> None:
    reason = "Error in report request: a required reportOption is missing."

    message = ReportPollingRequester._report_options_error_message("GET_VENDOR_SALES_REPORT", reason)

    assert "Add the options under Report Options" in message
    assert "Amazon documents reportPeriod, distributorView, sellingProgram as required" in message
    assert "Check the values set" not in message
