#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_shopify.auth import ShopifyAuthenticator
from source_shopify.source import Products, ShopifyDeletedEventsStream


@pytest.fixture
def config(basic_config):
    basic_config["start_date"] = "2020-11-01"
    basic_config["authenticator"] = ShopifyAuthenticator(basic_config)
    return basic_config


@pytest.mark.parametrize(
    "stream,expected_main_path,expected_events_path",
    [
        (Products, "products.json", "events.json"),
    ],
)
def test_path(stream, expected_main_path, expected_events_path, config):
    stream = stream(config)
    main_path = stream.path()
    events_path = stream.deleted_events.path()
    assert main_path == expected_main_path
    assert events_path == expected_events_path


@pytest.mark.parametrize(
    "stream,expected_events_schema",
    [
        (Products, {}),
    ],
)
def test_get_json_schema(stream, expected_events_schema, config):
    stream = stream(config)
    schema = stream.deleted_events.get_json_schema()
    # no schema is expected
    assert schema == expected_events_schema


@pytest.mark.parametrize(
    "stream,expected_data_field,expected_pk,expected_cursor_field",
    [
        (Products, "events", "id", "deleted_at"),
    ],
)
def test_has_correct_instance_vars(stream, expected_data_field, expected_pk, expected_cursor_field, config):
    stream = stream(config)
    assert stream.deleted_events.data_field == expected_data_field
    assert stream.deleted_events.primary_key == expected_pk
    assert stream.deleted_events.cursor_field == expected_cursor_field


@pytest.mark.parametrize(
    "stream,expected",
    [
        (Products, None),
    ],
)
def test_has_no_availability_strategy(stream, expected, config):
    stream = stream(config)
    # no availability_strategy is expected
    assert stream.deleted_events.availability_strategy is expected


@pytest.mark.parametrize(
    "stream,deleted_records_json,expected",
    [
        (
            Products,
            [
                {
                    "id": 123,
                    "subject_id": 234,
                    "created_at": "2023-09-05T14:02:00-07:00",
                    "subject_type": "Product",
                    "verb": "destroy",
                    "arguments": [],
                    "message": "Test Message",
                    "author": "Online Store",
                    "description": "Test Description",
                    "shop_url": "airbyte-integration-test",
                },
            ],
            [
                {
                    "id": 123,
                    "subject_id": 234,
                    "created_at": "2023-09-05T14:02:00-07:00",
                    "subject_type": "Product",
                    "verb": "destroy",
                    "arguments": [],
                    "message": "Test Message",
                    "author": "Online Store",
                    "description": "Test Description",
                    "shop_url": "airbyte-integration-test",
                },
            ],
        ),
    ],
)
def test_read_deleted_records(stream, requests_mock, deleted_records_json, expected, config, mocker):
    stream = stream(config)
    deleted_records_url = stream.url_base + stream.deleted_events.path()
    requests_mock.get(deleted_records_url, json=deleted_records_json)
    mocker.patch("source_shopify.source.IncrementalShopifyStreamWithDeletedEvents.read_records", return_value=deleted_records_json)
    assert list(stream.read_records(sync_mode=None)) == expected


@pytest.mark.parametrize(
    "stream,input,expected",
    [
        (
            Products,
            [
                {
                    "id": 123,
                    "subject_id": 234,
                    "created_at": "2023-09-05T14:02:00-07:00",
                    "subject_type": "Product",
                    "verb": "destroy",
                    "arguments": [],
                    "message": "Test Message",
                    "author": "Online Store",
                    "description": "Test Description",
                    "shop_url": "airbyte-integration-test",
                }
            ],
            [
                {
                    "id": 234,
                    "deleted_at": "2023-09-05T14:02:00-07:00",
                    "updated_at": "2023-09-05T14:02:00-07:00",
                    "deleted_message": "Test Message",
                    "deleted_description": "Test Description",
                    "shop_url": "airbyte-integration-test",
                }
            ],
        ),
    ],
)
def test_produce_deleted_records_from_events(stream, input, expected, config):
    stream = stream(config)
    result = stream.deleted_events.produce_deleted_records_from_events(input)
    assert list(result) == expected


@pytest.mark.parametrize(
    "stream, stream_state, next_page_token, expected_stream_params, expected_deleted_params",
    [
        # params with NO STATE
        (
            Products,
            {},
            None,
            {"limit": 250, "order": "updated_at asc", "updated_at_min": "2020-11-01"},
            {"filter": "Product", "verb": "destroy"},
        ),
        # params with STATE
        (
            Products,
            {"updated_at": "2028-01-01", "deleted": {"deleted_at": "2029-01-01"}},
            None,
            {"limit": 250, "order": "updated_at asc", "updated_at_min": "2028-01-01"},
            {"created_at_min": "2029-01-01", "filter": "Product", "verb": "destroy"},
        ),
        # params with NO STATE but with NEXT_PAGE_TOKEN
        (
            Products,
            {},
            {"page_info": "next_page_token"},
            {"limit": 250, "page_info": "next_page_token"},
            {"page_info": "next_page_token"},
        ),
    ],
)
def test_request_params(config, stream, stream_state, next_page_token, expected_stream_params, expected_deleted_params):
    stream = stream(config)
    assert stream.request_params(stream_state=stream_state, next_page_token=next_page_token) == expected_stream_params
    assert stream.deleted_events.request_params(stream_state=stream_state, next_page_token=next_page_token) == expected_deleted_params


@pytest.mark.parametrize(
    "stream,expected",
    [
        (Products, ShopifyDeletedEventsStream),
    ],
)
def test_deleted_events_instance(stream, config, expected):
    stream = stream(config)
    assert isinstance(stream.deleted_events, expected)


@pytest.mark.parametrize(
    "stream,expected",
    [
        (Products, ""),
    ],
)
def test_default_deleted_state_comparison_value(stream, config, expected):
    stream = stream(config)
    assert stream.default_deleted_state_comparison_value == expected


@pytest.mark.parametrize(
    "stream, last_record, current_state, expected",
    [
        # NO INITIAL STATE
        (
            Products,
            {"id": 1, "updated_at": "2021-01-01"},
            {},
            {"updated_at": "2021-01-01", "deleted": {"deleted_at": ""}},
        ),
        # with INITIAL STATE
        (
            Products,
            {"id": 1, "updated_at": "2022-01-01"},
            {"updated_at": "2021-01-01", "deleted": {"deleted_at": ""}},
            {"updated_at": "2022-01-01", "deleted": {"deleted_at": ""}},
        ),
        # with NO Last Record value and NO current state value
        (
            Products,
            {},
            {},
            {"updated_at": "", "deleted": {"deleted_at": ""}},
        ),
        # with NO Last Record value but with Current state value
        (
            Products,
            {},
            {"updated_at": "2030-01-01", "deleted": {"deleted_at": ""}},
            {"updated_at": "2030-01-01", "deleted": {"deleted_at": ""}},
        ),
    ],
)
def test_get_updated_state(config, stream, last_record, current_state, expected):
    stream = stream(config)
    assert stream.get_updated_state(current_state, last_record) == expected
