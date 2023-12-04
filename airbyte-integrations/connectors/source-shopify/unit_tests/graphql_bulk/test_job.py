#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from source_shopify.shopify_graphql.bulk.exceptions import ShopifyBulkExceptions
from source_shopify.streams.streams import MetafieldOrders


def test_get_errors_from_response(requests_mock, bulk_error, auth_config):
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=bulk_error)
    test_response = requests.get(stream.graphql_path)
    test_errors = stream.bulk_job.get_errors_from_response(test_response)
    assert test_errors == bulk_error.get("data").get("bulkOperationRunQuery").get("userErrors")


@pytest.mark.parametrize(
    "bulk_job_response, expected",
    [
        ("bulk_error_with_concurrent_job", True),
        ("bulk_successful_response", False),
    ],
)
def test_has_running_concurrent_job(request, requests_mock, bulk_job_response, auth_config, expected):
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.graphql_path)
    assert stream.bulk_job.has_running_concurrent_job(test_response) == expected
    
    
@pytest.mark.parametrize(
    "bulk_job_response, expected",
    [
        ("bulk_error", "[{'field': 'some_field', 'message': 'something wrong with the requested field.'}]"),
    ],
)
def test_job_check_for_errors(request, requests_mock, bulk_job_response, auth_config, expected):
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.graphql_path)
    with pytest.raises(ShopifyBulkExceptions.BulkJobError) as error:
        stream.bulk_job.job_check_for_errors(test_response)
    assert expected in repr(error.value)
    
    
@pytest.mark.parametrize(
    "bulk_job_response, expected",
    [
        ("bulk_successful_response", "gid://shopify/BulkOperation/4046733967549"),
        ("bulk_error", None)
    ],
)
def test_job_get_id(request, requests_mock, bulk_job_response, auth_config, expected):
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.graphql_path, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.graphql_path)
    assert stream.bulk_job.job_get_id(test_response) == expected
    

@pytest.mark.parametrize(
    "bulk_job_response, error_type, expected",
    [
        ("bulk_successful_response", None, "gid://shopify/BulkOperation/4046733967549"),
        ("bulk_error", ShopifyBulkExceptions.BulkJobError, "[{'field': 'some_field', 'message': 'something wrong with the requested field.'}]"),
        ("bulk_error_with_concurrent_job", None, None)
    ],
)
def test_job_create(request, requests_mock, bulk_job_response, auth_config, error_type, expected):
    stream = MetafieldOrders(auth_config)
    # patching concurent settings
    stream.bulk_job.concurrent_max_retry = 1 # 1 attempt max
    stream.bulk_job.concurrent_interval_sec = 1 # 1 sec
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
    "job_response, error_type, expected",
    [
        ("bulk_job_completed_response", None, 'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8''bulk-123456789.jsonl&response-content-type=application/jsonl'),
        ("bulk_job_failed_response", ShopifyBulkExceptions.BulkJobFailed, "exited with FAILED"),
        ("bulk_job_timeout_response", ShopifyBulkExceptions.BulkJobTimout, "exited with TIMEOUT"),
        ("bulk_job_access_denied_response", ShopifyBulkExceptions.BulkJobAccessDenied, "exited with ACCESS_DENIED"),
        ("bulk_job_unknown_status_response", ShopifyBulkExceptions.BulkJobUnknownError, "has unknown status"),
    ],
)
def test_job_check(mocker, request, requests_mock, job_response, auth_config, error_type, expected):
    stream = MetafieldOrders(auth_config)
    # get job_id from FIXTURE
    job_id = request.getfixturevalue(job_response).get("data").get("node").get("id")
    # patching the method to get the right ID checks
    mocker.patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkJob.job_get_id", value=job_id)
    # mocking the response for STATUS CHECKS
    requests_mock.post(stream.graphql_path, json=request.getfixturevalue(job_response))
    test_job_status_response = requests.post(stream.graphql_path)
    if error_type:
        with pytest.raises(error_type) as error:
            stream.bulk_job.job_check(stream.graphql_path, test_job_status_response)
        assert expected in repr(error.value)
    else:
        result = stream.bulk_job.job_check(stream.graphql_path, test_job_status_response)
        assert expected == result


def test_parse_response(mocker, requests_mock, jsonl_content_example, parse_response_expected_result, bulk_job_completed_response, auth_config):
    stream = MetafieldOrders(auth_config)
    # get the mocked job_result_url
    test_result_url = bulk_job_completed_response.get("data").get("node").get("url")
    # patching the method to return the `jpb_result_url` 
    mocker.patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkJob.job_check", return_value=test_result_url)
    # mocking the result url with jsonl content
    requests_mock.get(test_result_url, text=str(jsonl_content_example))
    # getting mock response
    test_bulk_respone = requests.get(test_result_url)
    test_records = stream.parse_response(test_bulk_respone)
    assert list(test_records) == [parse_response_expected_result]
    