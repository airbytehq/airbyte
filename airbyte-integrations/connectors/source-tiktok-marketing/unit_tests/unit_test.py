#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import random
from typing import Any, Dict, Iterable, List, Mapping, Tuple

import pendulum
import pytest
import requests_mock
import timeout_decorator
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from source_tiktok_marketing import SourceTiktokMarketing
from source_tiktok_marketing.streams import Ads, Advertisers, JsonUpdatedState

SANDBOX_CONFIG_FILE = "secrets/config.json"
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
def test_backoff(prepared_sandbox_args):
    """TiktokMarketing sends the header 'Retry-After' about needed delay.
    All streams have to handle it"""
    stream = Advertisers(**prepared_sandbox_args)
    with requests_mock.Mocker() as m:
        url = stream.url_base + stream.path()
        m.get(url, text=json.dumps({"code": 40100}))
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
                    "page_info": {
                        "total_number": total_number,
                        "page": page_number,
                        "page_size": page_size,
                        "total_page": len(page_items),
                    },
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
