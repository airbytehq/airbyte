#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import random
from urllib.parse import urlparse

import pendulum
import pytest
import requests
from source_zendesk_talk.streams import IVRMenus, IVRRoutes, ZendeskTalkIncrementalStream, ZendeskTalkSingleRecordStream, ZendeskTalkStream


class NonIncrementalStream(ZendeskTalkStream):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "/test_path"


class IncrementalStream(ZendeskTalkIncrementalStream):
    data_field = None
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "/test_path"


class SingleRecordStream(ZendeskTalkSingleRecordStream):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "/test_path"


def is_url(url: str) -> bool:
    """Checking if provided string is a correct URL, i.e. good enough for urlparse
    https://stackoverflow.com/a/52455972/656671
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@pytest.fixture(name="now")
def now_fixture(mocker):
    """Fixture to freeze the time"""
    return mocker.patch("source_zendesk_talk.streams.pendulum.now", return_value=pendulum.now())


class TestZendeskTalkStream:
    def test_url_base(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())

        assert "mydomain" in stream.url_base
        assert is_url(stream.url_base), "should be valid URL"

    def test_backoff_time(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())
        response = mocker.Mock(spec=requests.Response)
        response.headers = {"Retry-After": 10}

        result = stream.backoff_time(response)

        assert result == 10, "should return value from the header if set"

    def test_backoff_time_without_header(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())
        response = mocker.Mock(spec=requests.Response)
        response.headers = {}

        result = stream.backoff_time(response)

        assert result is None, "no backoff if the header is not set"

    def test_next_page_token(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())
        response = mocker.Mock(spec=requests.Response)
        response.json.return_value = {"next_page": "https://some.url.com?param1=20&param2=value"}

        result = stream.next_page_token(response)

        assert result == {"param1": ["20"], "param2": ["value"]}, "should return all params from the next_url"

    def test_next_page_token_end(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())
        response = mocker.Mock(spec=requests.Response)
        response.json.return_value = {"next_page": None}

        result = stream.next_page_token(response)

        assert result is None, "last page should return no token"

    def test_request_params(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())

        result = stream.request_params(stream_state={}, next_page_token={"some": "token"})

        assert result == {"some": "token"}

    def test_parse_response(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())
        response = mocker.Mock(spec=requests.Response)
        response.json.return_value = {stream.data_field: [{"record1"}, {"record2"}, {"record3"}], "some_other_data": 123}

        result = list(stream.parse_response(response=response))

        assert result == [{"record1"}, {"record2"}, {"record3"}]

    def test_parse_response_from_root(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())
        stream.data_field = None
        response = mocker.Mock(spec=requests.Response)
        response.json.return_value = [{"record1"}, {"record2"}, {"record3"}]

        result = list(stream.parse_response(response=response))

        assert result == [{"record1"}, {"record2"}, {"record3"}]

    def test_parse_response_single_object(self, mocker):
        stream = NonIncrementalStream(subdomain="mydomain", authenticator=mocker.Mock())
        response = mocker.Mock(spec=requests.Response)
        response.json.return_value = {stream.data_field: {"record1"}, "some_other_data": 123}

        result = list(stream.parse_response(response=response))

        assert result == [{"record1"}]


class TestZendeskTalkIncrementalStream:
    def test_get_updated_state_first_run(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)
        current_stream_state = {}
        latest_record = {stream.cursor_field: "2020-03-03T01:00:00Z", "some_attr": "value"}

        new_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)

        assert new_state == {stream.cursor_field: "2020-03-03T01:00:00Z"}

    def test_get_updated_state_desc_order(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)
        current_stream_state = {stream.cursor_field: "2020-03-03T02:00:00Z"}
        latest_record = {stream.cursor_field: "2020-03-03T01:00:00Z", "some_attr": "value"}

        new_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)

        assert new_state == {stream.cursor_field: "2020-03-03T02:00:00Z"}

    def test_get_updated_state_legacy_cursor(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)
        current_stream_state = {stream.legacy_cursor_field: "2020-03-03T02:00:00Z"}
        latest_record = {stream.cursor_field: "2020-03-03T01:00:00Z", "some_attr": "value"}

        new_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)

        assert new_state == {stream.cursor_field: "2020-03-03T02:00:00Z"}

    def test_get_updated_state(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)
        current_stream_state = {stream.cursor_field: "2020-03-03T02:00:00Z"}
        latest_record = {stream.cursor_field: "2020-03-03T03:00:00Z", "some_attr": "value"}

        new_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)

        assert new_state == {stream.cursor_field: "2020-03-03T03:00:00Z"}

    def test_request_params_first_page_without_state(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)

        result = stream.request_params(stream_state={})
        assert result == {stream.filter_param: int(start_date.timestamp())}, "should fallback to start_date"

    def test_request_params_first_page_with_state(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)

        result = stream.request_params(stream_state={stream.cursor_field: "2020-03-03T03:00:00Z"})
        assert result == {stream.filter_param: int(start_date.timestamp())}, "pick always bigger timestamp"

    def test_request_params_pagination(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)

        result = stream.request_params(
            stream_state={stream.cursor_field: "2020-03-03T03:00:00Z"},
            next_page_token={stream.filter_param: 12345},
        )
        assert result == {stream.filter_param: 12345}, "page token should always override"

    def test_next_page_token(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)
        response = mocker.Mock(spec=requests.Response, request=mocker.Mock(spec=requests.Request))
        response.json.return_value = {"next_page": f"https://some.url.com?param1=20&{stream.filter_param}=value1"}
        response.request.url = f"https://some.url.com?param1=30&{stream.filter_param}=value2"

        result = stream.next_page_token(response)
        assert result == {"param1": ["20"], stream.filter_param: ["value1"]}, "take page token from next_page"

    def test_next_page_token_empty_response(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)
        response = mocker.Mock(spec=requests.Response, request=mocker.Mock(spec=requests.Request))
        response.json.return_value = {"next_page": None}
        response.request.url = f"https://some.url.com?param1=30&{stream.filter_param}=value2"

        result = stream.next_page_token(response)
        assert result is None, "stop pagination if next page points to the current"

    def test_next_page_token_last_page(self, mocker):
        start_date = pendulum.now()
        stream = IncrementalStream(subdomain="mydomain", authenticator=mocker.Mock(), start_date=start_date)
        response = mocker.Mock(spec=requests.Response, request=mocker.Mock(spec=requests.Request))
        response.json.return_value = {"next_page": f"https://some.url.com?param1=20&{stream.filter_param}=value"}
        response.request.url = f"https://some.url.com?param1=30&{stream.filter_param}=value"

        result = stream.next_page_token(response)
        assert result is None, "stop pagination if next page points to the current"


class TestSingleRecordZendeskTalkStream:
    def test_parse_response(self, mocker, now):
        stream = SingleRecordStream(subdomain="mydomain", authenticator=mocker.Mock())
        response = mocker.Mock(spec=requests.Response)
        response.json.return_value = {stream.data_field: {"field1": "value", "field2": 3}, "some_other_data": 123}

        result = list(stream.parse_response(response=response))

        assert result == [{"field1": "value", "field2": 3, stream.primary_key: int(now().timestamp())}]


class TestIVRMenusStream:
    def test_ivr_menus_parse_response(self, mocker):
        stream = IVRMenus(subdomain="test-domain", authenticator=mocker.MagicMock())
        ivrs = [
            {"id": random.randint(10000, 99999), "menus": [dict(key="value")]},
            {"id": random.randint(10000, 99999), "menus": [dict(key="value")]},
            {"id": random.randint(10000, 99999), "menus": [dict(key="value")]},
            {"id": random.randint(10000, 99999), "menus": [dict(key="value")]},
        ]
        response_data = {"ivrs": ivrs}
        response = mocker.MagicMock()
        response.json.side_effect = [response_data]
        for i, menu in enumerate(stream.parse_response(response)):
            assert menu == {"ivr_id": ivrs[i]["id"], **ivrs[i]["menus"][0]}
        assert i + 1 == 4


class TestIVRRoutesStream:
    def test_ivr_menus_parse_response(self, mocker):
        stream = IVRRoutes(subdomain="test-domain", authenticator=mocker.MagicMock())
        ivr_routes = [
            {
                "id": 1,
                "menus": [
                    {"id": 1.1, "routes": [{"route": "1.1.1 route"}, {"route": "1.1.2 route"}]},
                    {"id": 1.2, "routes": [{"route": "1.2 route"}]},
                ],
            },
        ]
        response = mocker.MagicMock()
        response.json.side_effect = [{"ivrs": ivr_routes}]

        assert [record for record in stream.parse_response(response)] == [
            {"ivr_id": 1, "ivr_menu_id": 1.1, "id": 1.1, "routes": [{"route": "1.1.1 route"}, {"route": "1.1.2 route"}]},
            {"ivr_id": 1, "ivr_menu_id": 1.1, "id": 1.2, "routes": [{"route": "1.2 route"}]},
            {"ivr_id": 1, "ivr_menu_id": 1.2, "id": 1.1, "routes": [{"route": "1.1.1 route"}, {"route": "1.1.2 route"}]},
            {"ivr_id": 1, "ivr_menu_id": 1.2, "id": 1.2, "routes": [{"route": "1.2 route"}]},
        ]
