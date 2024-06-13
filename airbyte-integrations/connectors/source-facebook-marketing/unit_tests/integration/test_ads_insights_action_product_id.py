#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List, Optional, Union
from unittest import TestCase

import freezegun
import pendulum
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponse,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_protocol.models import AirbyteStateMessage, StreamDescriptor, SyncMode
from source_facebook_marketing.streams.async_job import Status

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, END_DATE, NOW, START_DATE, ConfigBuilder
from .pagination import NEXT_PAGE_TOKEN, FacebookMarketingPaginationStrategy
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, error_reduce_amount_of_data_response, get_account_response
from .utils import config, encode_request_body, read_output

_STREAM_NAME = "ads_insights_action_product_id"
_CURSOR_FIELD = "date_start"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"


def _update_api_throttle_limit_request(account_id: Optional[str] = ACCOUNT_ID) -> RequestBuilder:
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=account_id)


def _job_start_request(
    account_id: Optional[str] = ACCOUNT_ID, since: Optional[datetime] = None, until: Optional[datetime] = None
) -> RequestBuilder:
    since = since.strftime(DATE_FORMAT) if since else START_DATE[:10]
    until = until.strftime(DATE_FORMAT) if until else END_DATE[:10]
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "action_report_time": "mixed",
        "breakdowns": ["product_id"],
        "fields": [
            "account_currency",
            "account_id",
            "account_name",
            "action_values",
            "actions",
            "ad_click_actions",
            "ad_id",
            "ad_impression_actions",
            "ad_name",
            "adset_id",
            "adset_name",
            "attribution_setting",
            "auction_bid",
            "auction_competitiveness",
            "auction_max_competitor_bid",
            "buying_type",
            "campaign_id",
            "campaign_name",
            "canvas_avg_view_percent",
            "canvas_avg_view_time",
            "catalog_segment_actions",
            "catalog_segment_value",
            "catalog_segment_value_mobile_purchase_roas",
            "catalog_segment_value_omni_purchase_roas",
            "catalog_segment_value_website_purchase_roas",
            "clicks",
            "conversion_rate_ranking",
            "conversion_values",
            "conversions",
            "converted_product_quantity",
            "converted_product_value",
            "cost_per_15_sec_video_view",
            "cost_per_2_sec_continuous_video_view",
            "cost_per_action_type",
            "cost_per_ad_click",
            "cost_per_conversion",
            "cost_per_estimated_ad_recallers",
            "cost_per_inline_link_click",
            "cost_per_inline_post_engagement",
            "cost_per_outbound_click",
            "cost_per_thruplay",
            "cost_per_unique_action_type",
            "cost_per_unique_click",
            "cost_per_unique_inline_link_click",
            "cost_per_unique_outbound_click",
            "cpc",
            "cpm",
            "cpp",
            "created_time",
            "ctr",
            "date_start",
            "date_stop",
            "engagement_rate_ranking",
            "estimated_ad_recallers",
            "frequency",
            "full_view_impressions",
            "full_view_reach",
            "impressions",
            "inline_link_click_ctr",
            "inline_link_clicks",
            "inline_post_engagement",
            "instant_experience_clicks_to_open",
            "instant_experience_clicks_to_start",
            "instant_experience_outbound_clicks",
            "mobile_app_purchase_roas",
            "objective",
            "optimization_goal",
            "outbound_clicks",
            "outbound_clicks_ctr",
            "purchase_roas",
            "qualifying_question_qualify_answer_rate",
            "quality_ranking",
            "reach",
            "social_spend",
            "spend",
            "unique_actions",
            "unique_clicks",
            "unique_ctr",
            "unique_inline_link_click_ctr",
            "unique_inline_link_clicks",
            "unique_link_clicks_ctr",
            "unique_outbound_clicks",
            "unique_outbound_clicks_ctr",
            "updated_time",
            "video_15_sec_watched_actions",
            "video_30_sec_watched_actions",
            "video_avg_time_watched_actions",
            "video_continuous_2_sec_watched_actions",
            "video_p100_watched_actions",
            "video_p25_watched_actions",
            "video_p50_watched_actions",
            "video_p75_watched_actions",
            "video_p95_watched_actions",
            "video_play_actions",
            "video_play_curve_actions",
            "video_play_retention_0_to_15s_actions",
            "video_play_retention_20_to_60s_actions",
            "video_play_retention_graph_actions",
            "video_time_watched_actions",
            "website_ctr",
            "website_purchase_roas",
        ],
        "time_increment": 1,
        "action_attribution_windows": ["1d_click", "7d_click", "28d_click", "1d_view", "7d_view", "28d_view"],
        "filtering": [
            {
                "field": f"ad.effective_status",
                "operator": "IN",
                "value": [
                    "ACTIVE",
                    "ADSET_PAUSED",
                    "ARCHIVED",
                    "CAMPAIGN_PAUSED",
                    "DELETED",
                    "DISAPPROVED",
                    "IN_PROCESS",
                    "PAUSED",
                    "PENDING_BILLING_INFO",
                    "PENDING_REVIEW",
                    "PREAPPROVED",
                    "WITH_ISSUES"
                ],
            },
        ],
        "time_range": {"since": since, "until": until},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=account_id).with_body(encode_request_body(body))


def _job_status_request(report_run_ids: Union[str, List[str]]) -> RequestBuilder:
    if isinstance(report_run_ids, str):
        report_run_ids = [report_run_ids]
    body = {"batch": [{"method": "GET", "relative_url": f"{report_run_id}/"} for report_run_id in report_run_ids]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _get_insights_request(job_id: str) -> RequestBuilder:
    return RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=job_id).with_limit(100)


def _update_api_throttle_limit_response(api_throttle: Optional[int] = 0) -> HttpResponse:
    body = {}
    headers = {
        "x-fb-ads-insights-throttle": json.dumps(
            {"app_id_util_pct": api_throttle, "acc_id_util_pct": api_throttle, "ads_api_access_tier": "standard_access"}
        ),
    }
    return build_response(body=body, status_code=HTTPStatus.OK, headers=headers)


def _job_start_response(report_run_id: str) -> HttpResponse:
    body = {"report_run_id": report_run_id}
    return build_response(body=body, status_code=HTTPStatus.OK)


def _job_status_response(
    job_ids: Union[str, List[str]], status: Optional[Status] = Status.COMPLETED, account_id: Optional[str] = ACCOUNT_ID
) -> HttpResponse:
    if isinstance(job_ids, str):
        job_ids = [job_ids]
    body = [
        {
            "body": json.dumps({"id": job_id, "account_id": account_id, "async_status": status, "async_percent_completion": 100}),
        }
        for job_id in job_ids
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        pagination_strategy=FacebookMarketingPaginationStrategy(
            request=_get_insights_request(_JOB_ID).with_limit(100).build(), next_page_token=NEXT_PAGE_TOKEN
        ),
    )


def _ads_insights_action_product_id_record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        record_cursor_path=FieldPath(_CURSOR_FIELD),
    )


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        client_side_account_id = "123123123"
        server_side_account_id = "321321321"

        start_date = pendulum.parse(START_DATE)
        end_date = start_date + timedelta(hours=23)

        http_mocker.get(
            get_account_request(account_id=client_side_account_id).build(),
            get_account_response(account_id=server_side_account_id),
        )
        http_mocker.get(
            _update_api_throttle_limit_request(account_id=server_side_account_id).build(),
            _update_api_throttle_limit_response(),
        )
        http_mocker.post(
            _job_start_request(account_id=server_side_account_id, since=start_date, until=end_date).build(),
            _job_start_response(_REPORT_RUN_ID),
        )
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config().with_account_ids([client_side_account_id]).with_start_date(start_date).with_end_date(end_date))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_job_start_request().build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_pagination().with_record(_ads_insights_action_product_id_record()).build(),
        )
        http_mocker.get(
            _get_insights_request(_JOB_ID).with_next_page_token(NEXT_PAGE_TOKEN).build(),
            _insights_response()
            .with_record(_ads_insights_action_product_id_record())
            .with_record(_ads_insights_action_product_id_record())
            .build(),
        )

        output = self._read(config())
        assert len(output.records) == 3

    @HttpMocker()
    def test_given_api_throttle_exceeds_limit_on_first_check_when_read_then_wait_throttle_down_and_return_records(
        self, http_mocker: HttpMocker
    ) -> None:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            _update_api_throttle_limit_request().build(),
            [
                _update_api_throttle_limit_response(api_throttle=100),
                _update_api_throttle_limit_response(api_throttle=0),
            ],
        )
        http_mocker.post(_job_start_request().build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config())
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_multiple_days_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        start_date = NOW.subtract(days=1)
        end_date = NOW
        report_run_id_1 = "1571860060019500"
        report_run_id_2 = "4571860060019599"
        job_id_1 = "1049937379601600"
        job_id_2 = "1049937379601699"

        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_job_start_request(since=start_date, until=start_date).build(), _job_start_response(report_run_id_1))
        http_mocker.post(_job_start_request(since=end_date, until=end_date).build(), _job_start_response(report_run_id_2))
        http_mocker.post(_job_status_request([report_run_id_1, report_run_id_2]).build(), _job_status_response([job_id_1, job_id_2]))
        http_mocker.get(
            _get_insights_request(job_id_1).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )
        http_mocker.get(
            _get_insights_request(job_id_2).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config().with_start_date(start_date).with_end_date(end_date))
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_multiple_account_ids_when_read_then_return_records_from_all_accounts(self, http_mocker: HttpMocker) -> None:
        account_id_1 = "123123123"
        account_id_2 = "321321321"
        report_run_id_1 = "1571860060019500"
        report_run_id_2 = "4571860060019599"
        job_id_1 = "1049937379601600"
        job_id_2 = "1049937379601699"

        api_throttle_limit_response = _update_api_throttle_limit_response()

        http_mocker.get(get_account_request().with_account_id(account_id_1).build(), get_account_response(account_id=account_id_1))
        http_mocker.get(_update_api_throttle_limit_request().with_account_id(account_id_1).build(), api_throttle_limit_response)
        http_mocker.post(_job_start_request().with_account_id(account_id_1).build(), _job_start_response(report_run_id_1))
        http_mocker.post(_job_status_request(report_run_id_1).build(), _job_status_response(job_id_1, account_id=account_id_1))
        http_mocker.get(
            _get_insights_request(job_id_1).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        http_mocker.get(get_account_request().with_account_id(account_id_2).build(), get_account_response(account_id=account_id_2))
        http_mocker.get(_update_api_throttle_limit_request().with_account_id(account_id_2).build(), api_throttle_limit_response)
        http_mocker.post(_job_start_request().with_account_id(account_id_2).build(), _job_start_response(report_run_id_2))
        http_mocker.post(_job_status_request(report_run_id_2).build(), _job_status_response(job_id_2, account_id=account_id_2))
        http_mocker.get(
            _get_insights_request(job_id_2).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config().with_account_ids([account_id_1, account_id_2]))
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_status_500_reduce_amount_of_data_when_read_then_limit_reduced(self, http_mocker: HttpMocker) -> None:
        limit = 100

        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_job_start_request().build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).with_limit(limit).build(),
            error_reduce_amount_of_data_response(),
        )
        http_mocker.get(
            _get_insights_request(_JOB_ID).with_limit(int(limit / 2)).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        self._read(config())


@freezegun.freeze_time(NOW.isoformat())
class TestIncremental(TestCase):
    @staticmethod
    def _read(
        config_: ConfigBuilder, state: Optional[List[AirbyteStateMessage]] = None, expecting_exception: bool = False
    ) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.incremental,
            state=state,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_when_read_then_state_message_produced_and_state_match_start_interval(self, http_mocker: HttpMocker) -> None:
        account_id = "123123123"
        start_date = NOW.set(hour=0, minute=0, second=0)
        end_date = NOW.set(hour=23, minute=59, second=59)

        http_mocker.get(get_account_request().with_account_id(account_id).build(), get_account_response(account_id=account_id))
        http_mocker.get(
            _update_api_throttle_limit_request().with_account_id(account_id).build(),
            _update_api_throttle_limit_response(),
        )
        http_mocker.post(
            _job_start_request(since=start_date, until=end_date).with_account_id(account_id).build(),
            _job_start_response(_REPORT_RUN_ID),
        )
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID, account_id=account_id))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config().with_account_ids([account_id]).with_start_date(start_date).with_end_date(end_date))
        cursor_value_from_state_message = output.most_recent_state.stream_state.dict().get(account_id, {}).get(_CURSOR_FIELD)
        assert output.most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert cursor_value_from_state_message == start_date.strftime(DATE_FORMAT)

    @HttpMocker()
    def test_given_multiple_account_ids_when_read_then_state_produced_by_account_id_and_state_match_start_interval(
        self, http_mocker: HttpMocker
    ) -> None:
        account_id_1 = "123123123"
        account_id_2 = "321321321"
        start_date = NOW.set(hour=0, minute=0, second=0)
        end_date = NOW.set(hour=23, minute=59, second=59)
        report_run_id_1 = "1571860060019500"
        report_run_id_2 = "4571860060019599"
        job_id_1 = "1049937379601600"
        job_id_2 = "1049937379601699"

        api_throttle_limit_response = _update_api_throttle_limit_response()

        http_mocker.get(get_account_request().with_account_id(account_id_1).build(), get_account_response(account_id=account_id_1))
        http_mocker.get(_update_api_throttle_limit_request().with_account_id(account_id_1).build(), api_throttle_limit_response)
        http_mocker.post(
            _job_start_request(since=start_date, until=end_date).with_account_id(account_id_1).build(),
            _job_start_response(report_run_id_1),
        )
        http_mocker.post(_job_status_request(report_run_id_1).build(), _job_status_response(job_id_1, account_id=account_id_1))
        http_mocker.get(
            _get_insights_request(job_id_1).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        http_mocker.get(get_account_request().with_account_id(account_id_2).build(), get_account_response(account_id=account_id_2))
        http_mocker.get(_update_api_throttle_limit_request().with_account_id(account_id_2).build(), api_throttle_limit_response)
        http_mocker.post(
            _job_start_request(since=start_date, until=end_date).with_account_id(account_id_2).build(),
            _job_start_response(report_run_id_2),
        )
        http_mocker.post(_job_status_request(report_run_id_2).build(), _job_status_response(job_id_2, account_id=account_id_2))
        http_mocker.get(
            _get_insights_request(job_id_2).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config().with_account_ids([account_id_1, account_id_2]).with_start_date(start_date).with_end_date(end_date))
        cursor_value_from_state_account_1 = output.most_recent_state.stream_state.dict().get(account_id_1, {}).get(_CURSOR_FIELD)
        cursor_value_from_state_account_2 = output.most_recent_state.stream_state.dict().get(account_id_2, {}).get(_CURSOR_FIELD)
        expected_cursor_value = start_date.strftime(DATE_FORMAT)
        assert output.most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert cursor_value_from_state_account_1 == expected_cursor_value
        assert cursor_value_from_state_account_2 == expected_cursor_value
