#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import MagicMock

from pytest import fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


@fixture
def test_config() -> Mapping[str, str]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "start_date": "2021-05-07",
    }


@fixture
def wrong_date_config() -> Mapping[str, str]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "start_date": "wrong_date_format",
    }


@fixture
def wrong_account_id_config() -> Mapping[str, str]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "start_date": "2024-01-01",
        "account_id": "invalid_account",
    }


@fixture
def test_incremental_config() -> Mapping[str, Any]:
    return {
        "authenticator": MagicMock(),
        "start_date": "2021-05-07",
    }


@fixture
def test_current_stream_state() -> Mapping[str, str]:
    return {"updated_time": "2021-10-22"}


@fixture
def test_record() -> Mapping[str, Any]:
    return {"items": [{}], "bookmark": "string"}


@fixture
def test_record_filter() -> Mapping[str, Any]:
    return {"items": [{"updated_time": "2021-11-01"}], "bookmark": "string"}


@fixture
def test_response(test_record) -> MagicMock:
    response = MagicMock()
    response.json.return_value = test_record
    return response


@fixture
def test_response_single_account() -> MagicMock:
    response = MagicMock()
    response.json.return_value = {"id": "1234"}
    return response


@fixture
def analytics_report_stream() -> Any:
    return get_stream_by_name(
        "campaign_analytics_report",
        {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "start_date": "2021-05-07",
        },
    )


@fixture
def date_range() -> Mapping[str, Any]:
    return {"start_date": "2023-01-01", "end_date": "2023-01-31", "parent": {"id": "123"}}


@fixture(autouse=True)
def mock_auth(requests_mock) -> None:
    requests_mock.post(
        url="https://api.pinterest.com/v5/oauth/token",
        json={"access_token": "access_token", "expires_in": 3600},
    )


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = get_source(config)
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def read_from_stream(cfg, stream: str, sync_mode, state=None, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(cfg, state), cfg, catalog, state, expecting_exception)


def get_analytics_columns() -> str:
    # https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics
    analytics_columns = [
        "ADVERTISER_ID",  #
        "AD_ACCOUNT_ID",
        "AD_GROUP_ENTITY_STATUS",
        "AD_GROUP_ID",
        "AD_ID",
        "CAMPAIGN_DAILY_SPEND_CAP",
        "CAMPAIGN_ENTITY_STATUS",
        "CAMPAIGN_ID",
        "CAMPAIGN_LIFETIME_SPEND_CAP",
        "CAMPAIGN_NAME",
        "CHECKOUT_ROAS",
        "CLICKTHROUGH_1",  #
        "CLICKTHROUGH_1_GROSS",  #
        "CLICKTHROUGH_2",  #
        "CPC_IN_MICRO_DOLLAR",
        "CPM_IN_DOLLAR",
        "CPM_IN_MICRO_DOLLAR",
        "CTR",
        "CTR_2",
        "ECPCV_IN_DOLLAR",
        "ECPCV_P95_IN_DOLLAR",
        "ECPC_IN_DOLLAR",
        "ECPC_IN_MICRO_DOLLAR",
        "ECPE_IN_DOLLAR",
        "ECPM_IN_MICRO_DOLLAR",
        "ECPV_IN_DOLLAR",
        "ECTR",
        "EENGAGEMENT_RATE",
        "ENGAGEMENT_1",  #
        "ENGAGEMENT_2",  #
        "ENGAGEMENT_RATE",
        "IDEA_PIN_PRODUCT_TAG_VISIT_1",
        "IDEA_PIN_PRODUCT_TAG_VISIT_2",
        "IMPRESSION_1",
        "IMPRESSION_1_GROSS",
        "IMPRESSION_2",
        "INAPP_CHECKOUT_COST_PER_ACTION",
        "OUTBOUND_CLICK_1",
        "OUTBOUND_CLICK_2",
        "PAGE_VISIT_COST_PER_ACTION",
        "PAGE_VISIT_ROAS",
        "PAID_IMPRESSION",
        "PIN_ID",  #
        "PIN_PROMOTION_ID",  #
        "REPIN_1",  #
        "REPIN_2",  #
        "REPIN_RATE",
        "SPEND_IN_DOLLAR",
        "SPEND_IN_MICRO_DOLLAR",
        "TOTAL_CHECKOUT",
        "TOTAL_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_CLICKTHROUGH",
        "TOTAL_CLICK_ADD_TO_CART",  #
        "TOTAL_CLICK_CHECKOUT",
        "TOTAL_CLICK_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_CLICK_LEAD",  #
        "TOTAL_CLICK_SIGNUP",
        "TOTAL_CLICK_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_CONVERSIONS",
        "TOTAL_CUSTOM",  #
        "TOTAL_ENGAGEMENT",  #
        "TOTAL_ENGAGEMENT_CHECKOUT",
        "TOTAL_ENGAGEMENT_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_ENGAGEMENT_LEAD",  #
        "TOTAL_ENGAGEMENT_SIGNUP",
        "TOTAL_ENGAGEMENT_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_IDEA_PIN_PRODUCT_TAG_VISIT",
        "TOTAL_IMPRESSION_FREQUENCY",
        "TOTAL_IMPRESSION_USER",
        "TOTAL_LEAD",  #
        "TOTAL_OFFLINE_CHECKOUT",  #
        "TOTAL_PAGE_VISIT",
        "TOTAL_REPIN_RATE",
        "TOTAL_SIGNUP",
        "TOTAL_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_VIDEO_3SEC_VIEWS",
        "TOTAL_VIDEO_AVG_WATCHTIME_IN_SECOND",
        "TOTAL_VIDEO_MRC_VIEWS",
        "TOTAL_VIDEO_P0_COMBINED",
        "TOTAL_VIDEO_P100_COMPLETE",
        "TOTAL_VIDEO_P25_COMBINED",
        "TOTAL_VIDEO_P50_COMBINED",
        "TOTAL_VIDEO_P75_COMBINED",
        "TOTAL_VIDEO_P95_COMBINED",
        "TOTAL_VIEW_ADD_TO_CART",  #
        "TOTAL_VIEW_CHECKOUT",
        "TOTAL_VIEW_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_VIEW_LEAD",  #
        "TOTAL_VIEW_SIGNUP",
        "TOTAL_VIEW_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_CHECKOUT",
        "TOTAL_WEB_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_CLICK_CHECKOUT",
        "TOTAL_WEB_CLICK_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_ENGAGEMENT_CHECKOUT",
        "TOTAL_WEB_ENGAGEMENT_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_SESSIONS",  #
        "TOTAL_WEB_VIEW_CHECKOUT",
        "TOTAL_WEB_VIEW_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "VIDEO_3SEC_VIEWS_2",
        "VIDEO_LENGTH",  #
        "VIDEO_MRC_VIEWS_2",
        "VIDEO_P0_COMBINED_2",
        "VIDEO_P100_COMPLETE_2",
        "VIDEO_P25_COMBINED_2",
        "VIDEO_P50_COMBINED_2",
        "VIDEO_P75_COMBINED_2",
        "VIDEO_P95_COMBINED_2",
        "WEB_CHECKOUT_COST_PER_ACTION",
        "WEB_CHECKOUT_ROAS",
        "WEB_SESSIONS_1",  #
        "WEB_SESSIONS_2",  #
    ]
    return ",".join(analytics_columns)
