#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from source_shopify.shopify_graphql.bulk.exceptions import ShopifyBulkExceptions
from source_shopify.streams.streams import (
    Collections,
    DiscountCodes,
    FulfillmentOrders,
    InventoryItems,
    InventoryLevels,
    MetafieldOrders,
    TransactionsGraphql,
)


@pytest.mark.parametrize(
    "bulk_job_response, expected_len",
    [
        ("bulk_error", 1),
        ("bulk_unknown_error", 1),
        ("bulk_no_errors", 0),        
    ],
)
def test_get_errors_from_response(request, requests_mock, bulk_job_response, expected_len, auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.graphql_path)
    test_errors = stream.bulk_job.get_errors_from_response(test_response)
    assert len(test_errors) == expected_len


@pytest.mark.parametrize(
    "bulk_job_response, expected",
    [
        ("bulk_error_with_concurrent_job", True),
        ("bulk_successful_response", False),
        ("bulk_error", False),
    ],
)
def test_has_running_concurrent_job(request, requests_mock, bulk_job_response, auth_config, expected) -> None:
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.graphql_path)
    test_errors = stream.bulk_job.get_errors_from_response(test_response)
    assert stream.bulk_job.has_running_concurrent_job(test_errors) == expected


@pytest.mark.parametrize(
    "bulk_job_response, expected",
    [
        ("bulk_error", "[{'field': 'some_field', 'message': 'something wrong with the requested field.'}]"),
    ],
)
def test_job_check_for_errors(request, requests_mock, bulk_job_response, auth_config, expected) -> None:
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.graphql_path)
    test_errors = stream.bulk_job.get_errors_from_response(test_response)
    with pytest.raises(ShopifyBulkExceptions.BulkJobError) as error:
        stream.bulk_job.job_check_for_errors(test_errors)
    assert expected in repr(error.value)


@pytest.mark.parametrize(
    "bulk_job_response, expected",
    [
        ("bulk_successful_response", "gid://shopify/BulkOperation/4046733967549"), 
        ("bulk_error", None),
        ("bulk_successful_response_with_no_id", None),
    ],
)
def test_job_get_id(request, requests_mock, bulk_job_response, auth_config, expected) -> None:
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.graphql_path)
    assert stream.bulk_job.job_get_id(test_response) == expected


@pytest.mark.parametrize(
    "bulk_job_response, error_type, expected",
    [
        ("bulk_successful_response", None, "gid://shopify/BulkOperation/4046733967549"),
        (
            "bulk_error",
            ShopifyBulkExceptions.BulkJobError,
            "[{'field': 'some_field', 'message': 'something wrong with the requested field.'}]",
        ),
        ("bulk_error_with_concurrent_job", None, None),
    ],
)
def test_job_create(request, requests_mock, bulk_job_response, auth_config, error_type, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # patching concurent settings
    stream.bulk_job.concurrent_max_retry = 1  # 1 attempt max
    stream.bulk_job.concurrent_interval_sec = 1  # 1 sec
    #
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    if error_type:
        with pytest.raises(error_type) as error:
            stream.bulk_job.job_create(requests.get(stream.graphql_path).request)
        assert expected in repr(error.value)
    else:
        result = stream.bulk_job.job_create(requests.get(stream.graphql_path).request)
        assert stream.bulk_job.job_get_id(result) == expected


@pytest.mark.parametrize(
    "job_response, error_type, is_test, should_mock_id, expected",
    [
        (
            "bulk_job_completed_response",
            None,
            False,
            'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8'
            "bulk-123456789.jsonl&response-content-type=application/jsonl",
        ),
        ("bulk_job_failed_response", ShopifyBulkExceptions.BulkJobFailed, False, "exited with FAILED"),
        ("bulk_job_timeout_response", ShopifyBulkExceptions.BulkJobTimout, False, "exited with TIMEOUT"),
        ("bulk_job_access_denied_response", ShopifyBulkExceptions.BulkJobAccessDenied, False, "exited with ACCESS_DENIED"),
        # is_test should be set to `True` to exit from the while loop in `job_check_status()` 
        ("bulk_job_running_response", None, True, None),
        ("bulk_job_running_response_without_id", None, True, None),
    ],
)
def test_job_check(mocker, request, requests_mock, job_response, auth_config, error_type, is_test, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # modify the sleep time for the test
    stream.bulk_job.job_check_interval_sec = 1
    is_test = is_test if is_test else False
    # get job_id from FIXTURE
    job_id = request.getfixturevalue(job_response).get("data").get("node").get("id")
    # patching the method to get the right ID checks
    if job_id:
        mocker.patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkJob.job_get_id", value=job_id)
    # mocking the response for STATUS CHECKS
    requests_mock.post(stream.graphql_path, json=request.getfixturevalue(job_response))
    test_job_status_response = requests.post(stream.graphql_path)
    if error_type:
        with pytest.raises(error_type) as error:
            stream.bulk_job.job_check(stream.graphql_path, test_job_status_response, is_test)
        assert expected in repr(error.value)
    else:
        result = stream.bulk_job.job_check(stream.graphql_path, test_job_status_response, is_test)
        assert expected == result


@pytest.mark.parametrize(
    "stream, json_content_example, expected",
    [
        (MetafieldOrders, "metafield_jsonl_content_example", "metafield_parse_response_expected_result"),
        (FulfillmentOrders, "filfillment_order_jsonl_content_example", "fulfillment_orders_response_expected_result"),
        (DiscountCodes, "discount_codes_jsonl_content_example", "discount_codes_response_expected_result"),
        (Collections, "collections_jsonl_content_example", "collections_response_expected_result"),
        (TransactionsGraphql, "transactions_jsonl_content_example", "transactions_response_expected_result"),
        (InventoryItems, "inventory_items_jsonl_content_example", "inventory_items_response_expected_result"),
        (InventoryLevels, "inventory_levels_jsonl_content_example", "inventory_levels_response_expected_result"),
    ],
    ids=[
        "MetafieldOrders",
        "FulfillmentOrders",
        "DiscountCodes",
        "Collections",
        "TransactionsGraphql",
        "InventoryItems",
        "InventoryLevels",
    ],
)
def test_bulk_stream_parse_response(
    mocker,
    request,
    requests_mock,
    bulk_job_completed_response,
    stream,
    json_content_example,
    expected,
    auth_config,
) -> None:
    stream = stream(auth_config)
    # get the mocked job_result_url
    test_result_url = bulk_job_completed_response.get("data").get("node").get("url")
    # patching the method to return the `job_result_url`
    mocker.patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkJob.job_check", return_value=test_result_url)
    # mocking the result url with jsonl content
    requests_mock.get(test_result_url, text=request.getfixturevalue(json_content_example))
    # getting mock response
    test_bulk_response: requests.Response = requests.get(test_result_url)
    test_records = list(stream.parse_response(test_bulk_response))
    expected_result = request.getfixturevalue(expected)
    if isinstance(expected_result, dict):
        assert test_records == [expected_result]
    elif isinstance(expected_result, list):
        assert test_records == expected_result
