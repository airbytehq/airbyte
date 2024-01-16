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
    requests_mock.get(stream.bulk_job.base_url, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.bulk_job.base_url)
    test_errors = stream.bulk_job.get_errors_from_response(test_response)
    assert len(test_errors) == expected_len


def test_get_errors_from_response_invalid_response(auth_config) -> None:
    expected = "Couldn't check the `response` for `errors`"
    stream = MetafieldOrders(auth_config)
    response = requests.Response()
    response.status_code = 404
    response.url = "https://example.com/invalid"
    with pytest.raises(ShopifyBulkExceptions.BulkJobBadResponse) as error:
        stream.bulk_job.get_errors_from_response(response)
    assert expected in repr(error.value)


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
    requests_mock.get(stream.bulk_job.base_url, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.bulk_job.base_url)
    test_errors = stream.bulk_job.get_errors_from_response(test_response)
    assert stream.bulk_job.has_running_concurrent_job(test_errors) == expected


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
    requests_mock.get(stream.bulk_job.base_url, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.bulk_job.base_url)
    assert stream.bulk_job.job_get_id(test_response) == expected


@pytest.mark.parametrize(
    "bulk_job_response, error_type, expected",
    [
        ("bulk_successful_response", None, "gid://shopify/BulkOperation/4046733967549"),
        ("bulk_error_with_concurrent_job", None, None),
    ],
)
def test_job_create(request, requests_mock, bulk_job_response, auth_config, error_type, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # patching concurent settings
    stream.bulk_job.concurrent_max_retry = 1  # 1 attempt max
    stream.bulk_job.concurrent_interval_sec = 1  # 1 sec
    
    requests_mock.get(stream.bulk_job.base_url, json=request.getfixturevalue(bulk_job_response))
    result = stream.bulk_job._job_create(requests.get(stream.bulk_job.base_url).request)
    assert stream.bulk_job.job_get_id(result) == expected


@pytest.mark.parametrize(
    "bulk_job_response, concurrent_max_retry, expected",
    [
        # method should return this response fixture, once retried.
        ("bulk_successful_completed_response", 2, "gid://shopify/BulkOperation/4046733967549"),
        # method should return None, because the concurrent BULK Job is in progress
        ("bulk_error_with_concurrent_job", 1, None),
    ],
    ids=[
        "regular concurrent request",
        "max atttempt reached",
    ]
)
def test_job_retry_on_concurrency(request, requests_mock, bulk_job_response, concurrent_max_retry, auth_config, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # patching concurent settings
    stream.bulk_job.concurrent_max_retry = concurrent_max_retry
    stream.bulk_job.concurrent_interval_sec = 1
    
    requests_mock.get(stream.bulk_job.base_url, json=request.getfixturevalue(bulk_job_response))
    result = stream.bulk_job.job_retry_on_concurrency(requests.get(stream.bulk_job.base_url).request)
    if result:
        assert stream.bulk_job.job_get_id(result) == expected
    else:
        assert result == expected


@pytest.mark.parametrize(
    "job_response, error_type, path_healthcheck, is_test, expected",
    [
        (
            "bulk_job_completed_response",
            None,
            False,
            False,
            'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8'
            "bulk-123456789.jsonl&response-content-type=application/jsonl",
        ),
        ("bulk_job_failed_response", ShopifyBulkExceptions.BulkJobFailed, False, False, "exited with FAILED"),
        ("bulk_job_timeout_response", ShopifyBulkExceptions.BulkJobTimout, False, False, "exited with TIMEOUT"),
        ("bulk_job_access_denied_response", ShopifyBulkExceptions.BulkJobAccessDenied, False, False, "exited with ACCESS_DENIED"),
        ("bulk_successful_response_with_errors", ShopifyBulkExceptions.BulkJobUnknownError, True, False, "Could not validate the status of the BULK Job"),
        # is_test should be set to `True` to exit from the while loop in `job_check_status()`
        ("bulk_job_running_response", None, False, True, None),
        ("bulk_job_running_response_without_id", None, False, True, None),
        # bulk job with unknown status
        ("bulk_error_with_concurrent_job", None, False, False, None),
    ],
    ids=[
        "completed",
        "failed",
        "timeout",
        "access_denied",
        "success with errors (edge)",
        "running",
        "running_no_id (edge)",
        "concurrent request max attempt reached (edge)",
    ],
)
def test_job_check(mocker, request, requests_mock, job_response, auth_config, error_type, path_healthcheck, is_test, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # modify the sleep time for the test
    stream.bulk_job.concurrent_max_retry = 1
    stream.bulk_job.concurrent_interval_sec = 1
    stream.bulk_job.job_check_interval_sec = 5
    is_test = is_test if is_test else False
    # get job_id from FIXTURE
    job_id = request.getfixturevalue(job_response).get("data", {}).get("node", {}).get("id")
    # patching the method to get the right ID checks
    if job_id:
        mocker.patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkJob.job_get_id", value=job_id)
    if path_healthcheck:
        mocker.patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkJob.job_healthcheck", value=job_response)
    # mocking the response for STATUS CHECKS
    requests_mock.post(stream.bulk_job.base_url, json=request.getfixturevalue(job_response))
    test_job_status_response = requests.post(stream.bulk_job.base_url)
    if error_type:
        with pytest.raises(error_type) as error:
            stream.bulk_job.job_check(test_job_status_response, is_test)
        assert expected in repr(error.value)
    else:
        result = stream.bulk_job.job_check(test_job_status_response, is_test)
        assert expected == result


def test_job_record_producer_invalid_filename(mocker, auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    expected = "An error occured while producing records from BULK Job result"
    # patching the method to get the filename
    mocker.patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkJob.job_retrieve_result", value="test.jsonl")
    mocker.patch("source_shopify.shopify_graphql.bulk.record.ShopifyBulkRecord.produce_records", side_effect=Exception)
    with pytest.raises(ShopifyBulkExceptions.BulkRecordProduceError) as error:
        list(stream.bulk_job.job_record_producer(None))
    assert expected in repr(error.value)


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
