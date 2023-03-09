#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import random
from typing import Any, Dict, Iterable, List, Mapping, Tuple
from unittest.mock import patch

import pendulum
import pytest
import requests_mock
import timeout_decorator
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from source_tiktok_marketing import SourceTiktokMarketing
from source_tiktok_marketing.streams import Ads, Advertisers, JsonUpdatedState

SANDBOX_CONFIG_FILE = "secrets/sandbox_config.json"
PROD_CONFIG_FILE = "secrets/prod_config.json"


@pytest.fixture(scope="module")
def prepared_sandbox_args():
    """Generates streams settings from a file for sandbox"""
    with open(SANDBOX_CONFIG_FILE, "r") as f:
        return SourceTiktokMarketing._prepare_stream_args(json.loads(f.read()))


@pytest.fixture(scope="module")
def prepared_prod_args():
    """Generates streams settings from a file for production"""
    with open(PROD_CONFIG_FILE, "r") as f:
        return SourceTiktokMarketing._prepare_stream_args(json.loads(f.read()))


@timeout_decorator.timeout(20)
@pytest.mark.parametrize("error_code", (40100, 50002))
def test_backoff(prepared_sandbox_args, error_code):
    """TiktokMarketing sends the header 'Retry-After' about needed delay.
    All streams have to handle it"""
    stream = Advertisers(**prepared_sandbox_args)
    with requests_mock.Mocker() as m:
        url = stream.url_base + stream.path()
        m.get(url, text=json.dumps({"code": error_code}))
        with pytest.raises(UserDefinedBackoffException):
            list(stream.read_records(sync_mode=None))


def generate_pages(items: List[Mapping[str, Any]], page_size: int, last_empty: bool = False) -> Iterable[Tuple[int, Dict]]:
    pages = []
    for i in range(0, len(items), page_size):
        pages.append(items[i : i + page_size])
    if last_empty:
        pages.append([])
    total_number = len(items)
    for page_number, page_items in enumerate(pages, start=1):
        yield (
            page_number,
            {
                "message": "OK",
                "code": 0,
                "request_id": "unique_request_id",
                "data": {
                    "page_info": {"total_number": total_number, "page": page_number, "page_size": page_size, "total_page": len(page_items)},
                    "list": page_items,
                },
            },
        )


def random_integer(max_value: int = 1634125471, min_value: int = 1) -> int:
    return random.randint(min_value, max_value)


def unixtime2str(unix_time: int) -> str:
    "Converts unix time to string"
    return pendulum.from_timestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")


def test_random_items(prepared_prod_args):
    stream = Ads(**prepared_prod_args)
    advertiser_count = 100
    test_advertiser_ids = set([random_integer() for _ in range(advertiser_count)])
    advertiser_count = len(test_advertiser_ids)
    page_size = 100
    with requests_mock.Mocker() as m:
        # mock for advertisers' list
        advertisers = [{"advertiser_id": i, "advertiser_name": str(i)} for i in test_advertiser_ids]
        for _, page_response in generate_pages(items=advertisers, page_size=advertiser_count):
            m.register_uri("GET", "/open_api/v1.2/oauth2/advertiser/get/", json=page_response)
        stream = Ads(**prepared_prod_args)
        stream.page_size = page_size
        stream.get_advertiser_ids()
        assert not set(test_advertiser_ids).symmetric_difference(stream._advertiser_ids), "stream found not all  advertiser IDs"

        current_state = None
        max_updated_value = None
        for stream_slice in stream.stream_slices():
            advertiser_id = stream_slice["advertiser_id"]
            test_ad_ids = [random_integer() for _ in range(random_integer(max_value=999))]
            ad_items = []
            for ad_id in test_ad_ids:
                create_time = random_integer(min_value=1507901660)
                ad_items.append(
                    {
                        "create_time": unixtime2str(create_time),
                        "modify_time": unixtime2str(create_time + 60),
                        "advertiser_id": advertiser_id,
                        "ad_id": ad_id,
                    }
                )
                if not max_updated_value or max_updated_value < ad_items[-1][stream.cursor_field]:
                    max_updated_value = ad_items[-1][stream.cursor_field]

            # mock for ads
            for page, page_response in generate_pages(items=ad_items, page_size=page_size, last_empty=True):
                uri = f"/open_api/v1.2/ad/get/?page_size={page_size}&advertiser_id={advertiser_id}"
                if page != 1:
                    uri += f"&page={page}"
                m.register_uri("GET", uri, complete_qs=True, json=page_response)

            for record in stream.read_records(sync_mode=None, stream_slice=stream_slice):
                current_state = stream.get_updated_state(current_state, record)
                assert isinstance(current_state[stream.cursor_field], JsonUpdatedState), "state should be an  JsonUpdatedState object"
                if advertisers[-1]["advertiser_id"] != advertiser_id:
                    assert (
                        current_state[stream.cursor_field].dict() == ""
                    ), "max updated cursor value should be returned for last slice only"
        assert len(stream._advertiser_ids) == 0, "all advertisers should be popped"
        assert current_state[stream.cursor_field].dict() == max_updated_value


@pytest.mark.parametrize(
    "config, stream_len",
    [
        (PROD_CONFIG_FILE, 22),
        (SANDBOX_CONFIG_FILE, 16),
    ],
)
def test_source_streams(config, stream_len):
    with open(config) as f:
        config = json.load(f)
    streams = SourceTiktokMarketing().streams(config=config)
    assert len(streams) == stream_len


def test_source_spec():
    spec = SourceTiktokMarketing().spec(logger=None)
    assert isinstance(spec, ConnectorSpecification)


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "account_id": 123,
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00",
        "end_date": "2020-10-10T00:00:00",
    }
    return config


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_tiktok_marketing.source.logger")


def test_source_check_connection_ok(config, logger_mock):
    with patch.object(Advertisers, "read_records", return_value=iter([1])):
        assert SourceTiktokMarketing().check_connection(logger_mock, config=config) == (True, None)


def test_source_check_connection_failed(config, logger_mock):
    with patch.object(Advertisers, "read_records", return_value=0):
        assert SourceTiktokMarketing().check_connection(logger_mock, config=config)[0] is False


@pytest.mark.parametrize(
    "config_file",
    ["integration_tests/invalid_config_oauth.json", "integration_tests/invalid_config_access_token.json", "secrets/config.json"],
)
def test_source_prepare_stream_args(config_file):
    with open(config_file) as f:
        config = json.load(f)
        args = SourceTiktokMarketing._prepare_stream_args(config)
        assert "authenticator" in args
