# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import SyncMode

from .config import ACCOUNT_ID, ConfigBuilder
from .request_builder import get_account_request, get_ad_sets_request, get_ads_request, get_campaigns_request
from .response_builder import get_account_response, get_ad_sets_response, get_ads_response, get_campaigns_response
from .utils import config, read_output


class TestIncludeDeleted(TestCase):
    account_id = ACCOUNT_ID
    filter_statuses_flag = "filter_statuses"
    statuses = ["ACTIVE", "ARCHIVED"]

    @staticmethod
    def _read(config_: ConfigBuilder, stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=stream_name,
            sync_mode=SyncMode.incremental,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_ads_stream(self, http_mocker: HttpMocker):
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        filters = (
            '[{"field":"ad.effective_status","operator":"IN","value":["ACTIVE","ARCHIVED"]},'
            '{"field":"ad.updated_time","operator":"GREATER_THAN","value":1672531200}]'
        )
        fields = [
            "bid_type",
            "account_id",
            "campaign_id",
            "adset_id",
            "adlabels",
            "bid_amount",
            "bid_info",
            "status",
            "creative",
            "id",
            "updated_time",
            "created_time",
            "name",
            "targeting",
            "effective_status",
            "last_updated_by_app_id",
            "recommendations",
            "source_ad_id",
            "tracking_specs",
            "conversion_specs",
        ]

        http_mocker.get(
            get_ads_request().with_limit(100).with_filtering(filters).with_fields(fields).with_summary().build(),
            get_ads_response(),
        )

        output = self._read(config().with_ad_statuses(self.statuses), "ads")
        assert len(output.records) == 1
        account_state = output.most_recent_state.dict()["stream_state"][self.account_id]
        assert self.filter_statuses_flag in account_state, f"State should include `filter_statuses` flag"
        assert account_state == {"filter_statuses": ["ACTIVE", "ARCHIVED"], "updated_time": "2023-03-21T22:41:46-0700"}

    @HttpMocker()
    def test_campaigns_stream(self, http_mocker: HttpMocker):
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        filters = (
            '[{"field":"campaign.effective_status","operator":"IN","value":["ACTIVE","ARCHIVED"]},'
            '{"field":"campaign.updated_time","operator":"GREATER_THAN","value":1672531200}]'
        )
        fields = [
            "account_id",
            "adlabels",
            "bid_strategy",
            "boosted_object_id",
            "budget_rebalance_flag",
            "budget_remaining",
            "buying_type",
            "daily_budget",
            "created_time",
            "configured_status",
            "effective_status",
            "id",
            "issues_info",
            "lifetime_budget",
            "name",
            "objective",
            "smart_promotion_type",
            "source_campaign_id",
            "special_ad_category",
            "special_ad_category_country",
            "spend_cap",
            "start_time",
            "status",
            "stop_time",
            "updated_time",
        ]

        http_mocker.get(
            get_campaigns_request().with_limit(100).with_filtering(filters).with_fields(fields).with_summary().build(),
            get_campaigns_response(),
        )
        output = self._read(config().with_campaign_statuses(self.statuses), "campaigns")
        assert len(output.records) == 1

        account_state = output.most_recent_state.dict()["stream_state"][self.account_id]
        assert self.filter_statuses_flag in account_state, f"State should include `filter_statuses` flag"
        assert account_state == {"filter_statuses": ["ACTIVE", "ARCHIVED"], "updated_time": "2024-03-12T15:02:47-0700"}

    @HttpMocker()
    def test_ad_sets_stream(self, http_mocker: HttpMocker):
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        filters = (
            '[{"field":"adset.effective_status","operator":"IN","value":["ACTIVE","ARCHIVED"]},'
            '{"field":"adset.updated_time","operator":"GREATER_THAN","value":1672531200}]'
        )
        fields = [
            "name",
            "end_time",
            "promoted_object",
            "id",
            "account_id",
            "updated_time",
            "daily_budget",
            "budget_remaining",
            "effective_status",
            "campaign_id",
            "created_time",
            "start_time",
            "lifetime_budget",
            "targeting",
            "bid_info",
            "bid_strategy",
            "bid_amount",
            "bid_constraints",
            "adlabels",
        ]

        http_mocker.get(
            get_ad_sets_request().with_limit(100).with_filtering(filters).with_fields(fields).with_summary().build(),
            get_ad_sets_response(),
        )
        output = self._read(config().with_ad_set_statuses(self.statuses), "ad_sets")
        assert len(output.records) == 1

        account_state = output.most_recent_state.dict()["stream_state"][self.account_id]
        assert self.filter_statuses_flag in account_state, f"State should include `filter_statuses` flag"
        assert account_state == {"filter_statuses": ["ACTIVE", "ARCHIVED"], "updated_time": "2024-03-02T15:02:47-0700"}
