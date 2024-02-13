#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

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
from airbyte_protocol.models import AirbyteStateMessage, SyncMode
from source_facebook_marketing.streams.async_job import Status

from .config import ACCESS_TOKEN, ACCOUNT_ID, ConfigBuilder
from .pagination import FacebookMarketingPaginationStrategy
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, error_reduce_amount_of_data_response, get_account_response
from .utils import config, read_output

_STREAM_NAME = "ads_insights_action_product_id"
_CURSOR_FIELD = "date_start"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"


def _update_api_throttle_limit_request() -> RequestBuilder:
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID)


def _job_start_request() -> RequestBuilder:
    body = (
        "level=ad&action_breakdowns=%5B%5D&action_report_time=mixed&breakdowns=%5B%22product_id%22%5D&"
        "fields=%5B%22account_currency%22%2C%22account_id%22%2C%22account_name%22%2C%22action_values%22%2C%22"
        "actions%22%2C%22ad_click_actions%22%2C%22ad_id%22%2C%22ad_impression_actions%22%2C%22ad_name%22%2C%22"
        "adset_id%22%2C%22adset_name%22%2C%22age_targeting%22%2C%22attribution_setting%22%2C%22auction_bid%22%2C%22"
        "auction_competitiveness%22%2C%22auction_max_competitor_bid%22%2C%22buying_type%22%2C%22campaign_id%22%2C%22"
        "campaign_name%22%2C%22canvas_avg_view_percent%22%2C%22canvas_avg_view_time%22%2C%22"
        "catalog_segment_actions%22%2C%22catalog_segment_value%22%2C%22"
        "catalog_segment_value_mobile_purchase_roas%22%2C%22catalog_segment_value_omni_purchase_roas%22%2C%22"
        "catalog_segment_value_website_purchase_roas%22%2C%22clicks%22%2C%22conversion_rate_ranking%22%2C%22"
        "conversion_values%22%2C%22conversions%22%2C%22converted_product_quantity%22%2C%22"
        "converted_product_value%22%2C%22cost_per_15_sec_video_view%22%2C%22"
        "cost_per_2_sec_continuous_video_view%22%2C%22cost_per_action_type%22%2C%22cost_per_ad_click%22%2C%22"
        "cost_per_conversion%22%2C%22cost_per_estimated_ad_recallers%22%2C%22cost_per_inline_link_click%22%2C%22"
        "cost_per_inline_post_engagement%22%2C%22cost_per_outbound_click%22%2C%22cost_per_thruplay%22%2C%22"
        "cost_per_unique_action_type%22%2C%22cost_per_unique_click%22%2C%22cost_per_unique_inline_link_click%22%2C%22"
        "cost_per_unique_outbound_click%22%2C%22cpc%22%2C%22cpm%22%2C%22cpp%22%2C%22created_time%22%2C%22ctr%22%2C%22"
        "date_start%22%2C%22date_stop%22%2C%22engagement_rate_ranking%22%2C%22estimated_ad_recall_rate%22%2C%22"
        "estimated_ad_recall_rate_lower_bound%22%2C%22estimated_ad_recall_rate_upper_bound%22%2C%22"
        "estimated_ad_recallers%22%2C%22estimated_ad_recallers_lower_bound%22%2C%22"
        "estimated_ad_recallers_upper_bound%22%2C%22frequency%22%2C%22full_view_impressions%22%2C%22"
        "full_view_reach%22%2C%22gender_targeting%22%2C%22impressions%22%2C%22inline_link_click_ctr%22%2C%22"
        "inline_link_clicks%22%2C%22inline_post_engagement%22%2C%22instant_experience_clicks_to_open%22%2C%22"
        "instant_experience_clicks_to_start%22%2C%22instant_experience_outbound_clicks%22%2C%22labels%22%2C%22"
        "location%22%2C%22mobile_app_purchase_roas%22%2C%22objective%22%2C%22optimization_goal%22%2C%22"
        "outbound_clicks%22%2C%22outbound_clicks_ctr%22%2C%22purchase_roas%22%2C%22"
        "qualifying_question_qualify_answer_rate%22%2C%22quality_ranking%22%2C%22reach%22%2C%22social_spend%22%2C%22"
        "spend%22%2C%22unique_actions%22%2C%22unique_clicks%22%2C%22unique_ctr%22%2C%22"
        "unique_inline_link_click_ctr%22%2C%22unique_inline_link_clicks%22%2C%22unique_link_clicks_ctr%22%2C%22"
        "unique_outbound_clicks%22%2C%22unique_outbound_clicks_ctr%22%2C%22updated_time%22%2C%22"
        "video_15_sec_watched_actions%22%2C%22video_30_sec_watched_actions%22%2C%22"
        "video_avg_time_watched_actions%22%2C%22video_continuous_2_sec_watched_actions%22%2C%22"
        "video_p100_watched_actions%22%2C%22video_p25_watched_actions%22%2C%22video_p50_watched_actions%22%2C%22"
        "video_p75_watched_actions%22%2C%22video_p95_watched_actions%22%2C%22video_play_actions%22%2C%22"
        "video_play_curve_actions%22%2C%22video_play_retention_0_to_15s_actions%22%2C%22"
        "video_play_retention_20_to_60s_actions%22%2C%22video_play_retention_graph_actions%22%2C%22"
        "video_time_watched_actions%22%2C%22website_ctr%22%2C%22website_purchase_roas%22%2C%22wish_bid%22%5D&"
        "time_increment=1&action_attribution_windows=%5B%221d_click%22%2C%227d_click%22%2C%2228d_click%22%2C%221d_view"
        "%22%2C%227d_view%22%2C%2228d_view%22%5D&time_range=%7B%22since%22%3A%222023-01-01%22%2C%22"
        "until%22%3A%222023-01-01%22%7D"
    )
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(body)


def _job_status_request(report_run_id: str) -> RequestBuilder:
    body = f"batch=%5B%7B%22method%22%3A%22GET%22%2C%22relative_url%22%3A%22{report_run_id}%2F%22%7D%5D"
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(body)


def _get_insights_request(job_id: str) -> RequestBuilder:
    return RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=job_id).with_limit(100)


def _update_api_throttle_limit_response() -> HttpResponse:
    body = {}
    headers = {
        "x-fb-ads-insights-throttle": json.dumps(
            {"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}
        ),
    }
    return build_response(body=body, status_code=HTTPStatus.OK, headers=headers)


def _job_start_response(report_run_id: str) -> HttpResponse:
    body = {"report_run_id": report_run_id}
    return build_response(body=body, status_code=HTTPStatus.OK)


def _job_status_response(
    job_id: str, status: Optional[Status] = Status.COMPLETED, account_id: Optional[str] = ACCOUNT_ID
) -> HttpResponse:
    body = [
        {
            "body": json.dumps(
                {
                    "id": job_id, "account_id": account_id, "async_status": status, "async_percent_completion": 100
                }
            ),
        },
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        pagination_strategy=FacebookMarketingPaginationStrategy(_get_insights_request(_JOB_ID).with_limit(100).build()),
    )


def _ads_insights_action_product_id_record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        record_cursor_path=FieldPath(_CURSOR_FIELD),
    )


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
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_job_start_request().build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config())
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
            _get_insights_request(_JOB_ID).with_pagination_parameter().build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).with_record(
                _ads_insights_action_product_id_record()
            ).build(),
        )

        output = self._read(config())
        assert len(output.records) == 3

    @HttpMocker()
    def test_given_multiple_account_ids_when_read_then_return_records_from_all_accounts(
        self, http_mocker: HttpMocker
    ) -> None:
        account_id_1 = "123123123"
        account_id_2 = "321321321"
        report_run_id_1 = "1571860060019500"
        report_run_id_2 = "4571860060019599"
        job_id_1 = "1049937379601600"
        job_id_2 = "1049937379601699"

        api_throttle_limit_response = _update_api_throttle_limit_response()

        http_mocker.get(
            get_account_request().with_account_id(account_id_1).build(), get_account_response(account_id=account_id_1)
        )
        http_mocker.get(
            _update_api_throttle_limit_request().with_account_id(account_id_1).build(), api_throttle_limit_response
        )
        http_mocker.post(
            _job_start_request().with_account_id(account_id_1).build(), _job_start_response(report_run_id_1)
        )
        http_mocker.post(
            _job_status_request(report_run_id_1).build(), _job_status_response(job_id=job_id_1, account_id=account_id_1)
        )
        http_mocker.get(
            _get_insights_request(job_id_1).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        http_mocker.get(
            get_account_request().with_account_id(account_id_2).build(), get_account_response(account_id=account_id_2)
        )
        http_mocker.get(
            _update_api_throttle_limit_request().with_account_id(account_id_2).build(), api_throttle_limit_response
        )
        http_mocker.post(
            _job_start_request().with_account_id(account_id_2).build(), _job_start_response(report_run_id_2)
        )
        http_mocker.post(
            _job_status_request(report_run_id_2).build(), _job_status_response(job_id=job_id_2, account_id=account_id_2)
        )
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
    def test_when_read_then_state_message_produced_and_state_match_start_interval(
        self, http_mocker: HttpMocker
    ) -> None:
        account_id = "123123123"
        start_date = "2023-01-01T00:00:00Z"
        end_date = "2023-01-01T23:59:59Z"

        http_mocker.get(
            get_account_request().with_account_id(account_id).build(), get_account_response(account_id=account_id)
        )
        http_mocker.get(
            _update_api_throttle_limit_request().with_account_id(account_id).build(),
            _update_api_throttle_limit_response(),
        )
        http_mocker.post(_job_start_request().with_account_id(account_id).build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(
            _job_status_request(_REPORT_RUN_ID).build(), _job_status_response(job_id=_JOB_ID, account_id=account_id)
        )
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(config().with_account_ids([account_id]).with_start_date(start_date).with_end_date(end_date))
        cursor_value_from_state_message = output.most_recent_state.get(_STREAM_NAME, {}).get(account_id, {}).get(
            _CURSOR_FIELD
        )
        assert cursor_value_from_state_message == start_date[:10]

    @HttpMocker()
    def test_given_multiple_account_ids_when_read_then_state_produced_by_account_id_and_state_match_start_interval(
        self, http_mocker: HttpMocker
    ) -> None:
        account_id_1 = "123123123"
        account_id_2 = "321321321"
        start_date = "2023-01-01T00:00:00Z"
        end_date = "2023-01-01T23:59:59Z"
        report_run_id_1 = "1571860060019500"
        report_run_id_2 = "4571860060019599"
        job_id_1 = "1049937379601600"
        job_id_2 = "1049937379601699"

        api_throttle_limit_response = _update_api_throttle_limit_response()

        http_mocker.get(
            get_account_request().with_account_id(account_id_1).build(), get_account_response(account_id=account_id_1)
        )
        http_mocker.get(
            _update_api_throttle_limit_request().with_account_id(account_id_1).build(), api_throttle_limit_response
        )
        http_mocker.post(
            _job_start_request().with_account_id(account_id_1).build(), _job_start_response(report_run_id_1)
        )
        http_mocker.post(
            _job_status_request(report_run_id_1).build(), _job_status_response(job_id=job_id_1, account_id=account_id_1)
        )
        http_mocker.get(
            _get_insights_request(job_id_1).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        http_mocker.get(
            get_account_request().with_account_id(account_id_2).build(), get_account_response(account_id=account_id_2)
        )
        http_mocker.get(
            _update_api_throttle_limit_request().with_account_id(account_id_2).build(), api_throttle_limit_response
        )
        http_mocker.post(
            _job_start_request().with_account_id(account_id_2).build(), _job_start_response(report_run_id_2)
        )
        http_mocker.post(
            _job_status_request(report_run_id_2).build(), _job_status_response(job_id=job_id_2, account_id=account_id_2)
        )
        http_mocker.get(
            _get_insights_request(job_id_2).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = self._read(
            config().with_account_ids([account_id_1, account_id_2]).with_start_date(start_date).with_end_date(end_date)
        )
        cursor_value_from_state_account_1 = output.most_recent_state.get(_STREAM_NAME, {}).get(account_id_1, {}).get(
            _CURSOR_FIELD
        )
        cursor_value_from_state_account_2 = output.most_recent_state.get(_STREAM_NAME, {}).get(account_id_2, {}).get(
            _CURSOR_FIELD
        )
        expected_cursor_value = start_date[:10]
        assert cursor_value_from_state_account_1 == expected_cursor_value
        assert cursor_value_from_state_account_2 == expected_cursor_value
