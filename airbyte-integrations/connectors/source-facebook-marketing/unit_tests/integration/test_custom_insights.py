#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath, create_record_builder, create_response_builder, find_template

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .pagination import NEXT_PAGE_TOKEN, FacebookMarketingPaginationStrategy
from .request_builder import RequestBuilder, get_account_request
from .response_builder import get_account_response
from .test_ads_insights_action_product_id import (
    _get_insights_request,
    _job_start_response,
    _job_status_request,
    _job_status_response,
    _update_api_throttle_limit_request,
    _update_api_throttle_limit_response,
)
from .utils import config, encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_custom_insight"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_RESPONSE_TEMPLATE = "ads_insights_action_product_id"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["account_id", "ad_id", "actions", "date_start", "date_stop"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _FIELDS,
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _custom_insight(**overrides: Any) -> Dict[str, Any]:
    return {"name": _CUSTOM_INSIGHT_NAME, "fields": _FIELDS, "level": "ad", **overrides}


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_config, custom_insight_config, expected_windows",
    [
        pytest.param({"include_incrementality": True}, {}, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_only"),
        pytest.param(
            {"include_incrementality": True},
            {"include_incrementality": False},
            _DEFAULT_WINDOWS + ["incrementality"],
            id="top_level_enabled_custom_insight_default_false",
        ),
        pytest.param({}, {"include_incrementality": True}, _DEFAULT_WINDOWS + ["incrementality"], id="custom_insight_only"),
        pytest.param({"include_incrementality": False}, {"include_incrementality": False}, _DEFAULT_WINDOWS, id="disabled_everywhere"),
    ],
)
def test_custom_insight_job_request_includes_incrementality_window_from_top_level_or_custom_insight_config(
    top_level_config: Dict[str, Any], custom_insight_config: Dict[str, Any], expected_windows: List[str]
) -> None:
    """
    The top-level `include_incrementality` toggle must apply to custom insight streams too: the async
    insights job a custom insight stream starts has to request the `incrementality` attribution window
    when the option is enabled either at the top level or on the custom insight itself.
    """
    config_builder = config().with_custom_insights([_custom_insight(**custom_insight_config)])
    if "include_incrementality" in top_level_config:
        config_builder = config_builder.with_include_incrementality(top_level_config["include_incrementality"])

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        # HttpMocker matches the POST body exactly, so the read only finds a job (and a record) when the
        # connector sends exactly the expected `action_attribution_windows`.
        job_start_request = _job_start_request(expected_windows).build()
        http_mocker.post(job_start_request, _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            create_response_builder(
                response_template=find_template(_RESPONSE_TEMPLATE, __file__),
                records_path=FieldPath("data"),
                pagination_strategy=FacebookMarketingPaginationStrategy(
                    request=_get_insights_request(_JOB_ID).build(), next_page_token=NEXT_PAGE_TOKEN
                ),
            )
            .with_record(
                create_record_builder(response_template=find_template(_RESPONSE_TEMPLATE, __file__), records_path=FieldPath("data"))
            )
            .build(),
        )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(job_start_request, 1)
