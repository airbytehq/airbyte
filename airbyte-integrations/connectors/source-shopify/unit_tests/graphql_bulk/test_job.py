#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from os import remove

import pytest
import requests
from source_shopify.shopify_graphql.bulk.exceptions import ShopifyBulkExceptions
from source_shopify.shopify_graphql.bulk.status import ShopifyBulkJobStatus
from source_shopify.streams.streams import (
    Collections,
    CustomerAddress,
    CustomerJourneySummary,
    DiscountCodes,
    FulfillmentOrders,
    InventoryItems,
    InventoryLevels,
    MetafieldOrders,
    OrderRisks,
    ProductImages,
    Products,
    ProductVariants,
    TransactionsGraphql,
)

from airbyte_cdk.models import SyncMode


_ANY_SLICE = {}
_ANY_FILTER_FIELD = "any_filter_field"


def test_job_manager_default_values(auth_config) -> None:
    stream = Products(auth_config)

    # 10Mb chunk size to save the file
    assert stream.job_manager._retrieve_chunk_size == 10485760  # 1024 * 1024 * 10
    assert stream.job_manager._job_max_retries == 6
    assert stream.job_manager._job_backoff_time == 5
    # running job logger constrain, every 100-ish message will be printed
    assert stream.job_manager._log_job_msg_frequency == 100
    assert stream.job_manager._log_job_msg_count == 0
    # attempt counter
    assert stream.job_manager._concurrent_attempt == 0
    # sleep time per creation attempt
    assert stream.job_manager._concurrent_interval == 30
    # max attempts for job creation
    assert stream.job_manager._concurrent_max_retry == 120
    # currents: _job_id, _job_state, _job_created_at, _job_self_canceled
    assert not stream.job_manager._job_id
    # this string is based on ShopifyBulkJobStatus
    assert not stream.job_manager._job_state
    # completed and saved Bulk Job result filename
    assert not stream.job_manager._job_result_filename
    # date-time when the Bulk Job was created on the server
    assert not stream.job_manager._job_created_at
    # indicated whether or not we manually force-cancel the current job
    assert not stream.job_manager._job_self_canceled
    # time between job status checks
    assert stream.job_manager._job_check_interval == 3
    # 0.1 ~= P2H, default value, lower boundary for slice size
    assert stream.job_manager._job_size_min == 0.1
    # last running job object count
    assert stream.job_manager._job_last_rec_count == 0
    # how many records should be collected before we use the checkpoining
    assert stream.job_manager._job_checkpoint_interval == 200000
    # the flag to adjust the next slice from the checkpointed cursor vaue
    assert not stream.job_manager._job_adjust_slice_from_checkpoint
    # expand slice factor
    assert stream.job_manager._job_size_expand_factor == 2
    # reduce slice factor
    assert stream.job_manager._job_size_reduce_factor == 2
    # whether or not the slicer should revert the previous start value
    assert not stream.job_manager._job_should_revert_slice
    # 2 sec is set as default value to cover the case with the empty-fast-completed jobs
    assert stream.job_manager._job_last_elapsed_time == 2.0


def test_get_errors_from_response_invalid_response(auth_config) -> None:
    expected = "Couldn't check the `response` for `errors`"
    stream = MetafieldOrders(auth_config)
    response = requests.Response()
    response.status_code = 404
    response.url = "https://example.com/invalid"
    with pytest.raises(ShopifyBulkExceptions.BulkJobBadResponse) as error:
        stream.job_manager._job_healthcheck(response)
    assert expected in repr(error.value)


def test_retry_on_concurrent_job(request, requests_mock, auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    stream.job_manager._concurrent_interval = 0
    # mocking responses
    requests_mock.post(
        stream.job_manager.base_url,
        [
            # concurrent request is running (3 - retries)
            {"json": request.getfixturevalue("bulk_error_with_concurrent_job")},
            {"json": request.getfixturevalue("bulk_error_with_concurrent_job")},
            {"json": request.getfixturevalue("bulk_error_with_concurrent_job")},
            # concurrent request has finished
            {"json": request.getfixturevalue("bulk_successful_response")},
        ],
    )

    stream.job_manager.create_job(_ANY_SLICE, _ANY_FILTER_FIELD)
    # call count should be 4 (3 retries, 1 - succeeded)
    assert requests_mock.call_count == 4


@pytest.mark.parametrize(
    "bulk_job_response, concurrent_max_retry, error_type, expected",
    [
        # method should raise AirbyteTracebackException, because the concurrent BULK Job is in progress
        (
            "bulk_error_with_concurrent_job",
            1,
            ShopifyBulkExceptions.BulkJobConcurrentError,
            "The BULK Job couldn't be created at this time, since another job is running",
        ),
    ],
    ids=[
        "max attempt reached",
    ],
)
def test_job_retry_on_concurrency(
    request, requests_mock, bulk_job_response, concurrent_max_retry, error_type, auth_config, expected
) -> None:
    stream = MetafieldOrders(auth_config)
    # patching concurrent settings
    stream.job_manager._concurrent_max_retry = concurrent_max_retry
    stream.job_manager._concurrent_interval = 1

    requests_mock.post(stream.job_manager.base_url, json=request.getfixturevalue(bulk_job_response))

    if error_type:
        with pytest.raises(error_type) as error:
            stream.job_manager.create_job(_ANY_SLICE, _ANY_FILTER_FIELD)
        assert expected in repr(error.value) and requests_mock.call_count == 2
    else:
        # simulate the real job_id from created job
        stream.job_manager._job_id = expected
        stream.job_manager.create_job(_ANY_SLICE, _ANY_FILTER_FIELD)
        assert requests_mock.call_count == 2


@pytest.mark.parametrize(
    "bulk_job_response, expected",
    [
        ("bulk_successful_response", "gid://shopify/BulkOperation/4046733967549"),
        ("bulk_successful_response_with_no_id", None),
    ],
)
def test_job_process_created(request, requests_mock, bulk_job_response, auth_config, expected) -> None:
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.job_manager.base_url, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.job_manager.base_url)
    # process the job with id (typically CREATED one)
    stream.job_manager._job_process_created(test_response)
    assert stream.job_manager._job_id == expected


def test_job_state_completed(auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    stream.job_manager._job_state = ShopifyBulkJobStatus.COMPLETED.value
    assert stream.job_manager._job_completed() == True


@pytest.mark.parametrize(
    "job_response, error_type, expected",
    [
        ("bulk_job_completed_response", None, "bulk-123456789.jsonl"),
        ("bulk_job_failed_with_partial_url_response", None, "bulk-123456789.jsonl"),
        ("bulk_job_timeout_response", ShopifyBulkExceptions.BulkJobTimout, "exited with TIMEOUT"),
        ("bulk_job_access_denied_response", ShopifyBulkExceptions.BulkJobAccessDenied, "exited with ACCESS_DENIED"),
    ],
    ids=[
        "completed",
        "failed with partial result",
        "timeout",
        "access_denied",
    ],
)
def test_job_check_for_completion(mocker, request, requests_mock, job_response, auth_config, error_type, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # modify the sleep time for the test
    stream.job_manager._concurrent_max_retry = 1
    stream.job_manager._concurrent_interval = 1
    stream.job_manager._job_check_interval = 1
    # mocking the response for STATUS CHECKS
    requests_mock.post(stream.job_manager.base_url, json=request.getfixturevalue(job_response))
    test_job_status_response = requests.post(stream.job_manager.base_url)
    full_result_url = test_job_status_response.json().get("data", {}).get("node", {}).get("url")
    partial_result_url = test_job_status_response.json().get("data", {}).get("node", {}).get("partialDataUrl")
    job_result_url = full_result_url if full_result_url else partial_result_url
    if error_type:
        with pytest.raises(error_type) as error:
            list(stream.job_manager.job_get_results())
        assert expected in repr(error.value)
    else:
        if job_result_url:
            # mocking the nested request call to retrieve the data from result URL
            requests_mock.get(job_result_url, json=request.getfixturevalue(job_response))
        mocker.patch("source_shopify.shopify_graphql.bulk.record.ShopifyBulkRecord.read_file", return_value=[])
        stream.job_manager._job_check_state()
        assert expected == stream.job_manager._job_result_filename


@pytest.mark.parametrize(
    "job_response, error_type, expected",
    [
        ("bulk_job_failed_with_partial_url_response", ShopifyBulkExceptions.BulkJobFailed, "exited with FAILED"),
    ],
    ids=[
        "failed",
    ],
)
def test_job_failed_for_stream_with_no_bulk_checkpointing(
    mocker, request, requests_mock, job_response, error_type, expected, auth_config
) -> None:
    stream = InventoryLevels(auth_config)
    # modify the sleep time for the test
    stream.job_manager._concurrent_max_retry = 1
    stream.job_manager._concurrent_interval = 1
    stream.job_manager._job_check_interval = 1
    # mocking the response for STATUS CHECKS
    requests_mock.post(stream.job_manager.base_url, json=request.getfixturevalue(job_response))
    with pytest.raises(error_type) as error:
        # the test should raise an Error and make the stream `INCOMPLETE`,
        # another attempt will be taken with the new sync attempt.
        list(stream.job_manager.job_get_results())
    assert expected in repr(error.value)


@pytest.mark.parametrize(
    "job_response, job_state, error_type, max_retry, expected_msg, call_count_expected",
    [
        # No retry - dead end
        (
            "bulk_successful_response_with_errors",
            False,
            ShopifyBulkExceptions.BulkJobNonHandableError,
            2,
            "Non-handable error occured",
            1,
        ),
        # Should be retried
        (
            None,
            False,
            ShopifyBulkExceptions.BulkJobBadResponse,
            1,
            "Couldn't check the `response` for `errors`",
            2,
        ),
    ],
    ids=[
        "BulkJobNonHandableError",
        "BulkJobBadResponse",
    ],
)
def test_retry_on_job_creation_exception(
    request, requests_mock, auth_config, job_response, job_state, error_type, max_retry, call_count_expected, expected_msg
) -> None:
    stream = MetafieldOrders(auth_config)
    stream.job_manager._job_backoff_time = 0
    stream.job_manager._job_max_retries = max_retry
    # patching the method to get the right ID checks
    if job_response:
        stream.job_manager._job_id = request.getfixturevalue(job_response).get("data", {}).get("node", {}).get("id")

    if job_state:
        # setting job_state to simulate the error-in-the-middle
        stream.job_manager._job_state = request.getfixturevalue(job_response).get("data", {}).get("node", {}).get("status")

    # mocking the response for STATUS CHECKS
    json_mock_response = request.getfixturevalue(job_response) if job_response else None
    requests_mock.post(stream.job_manager.base_url, json=json_mock_response)

    # testing raised exception and backoff
    with pytest.raises(error_type) as error:
        stream.job_manager.create_job(_ANY_SLICE, _ANY_FILTER_FIELD)

    # we expect different call_count, because we set the different max_retries
    assert expected_msg in repr(error.value) and requests_mock.call_count == call_count_expected


@pytest.mark.parametrize(
    "job_response, expected",
    [
        ("bulk_job_created_response", ShopifyBulkJobStatus.CREATED.value),
        ("bulk_job_running_response", ShopifyBulkJobStatus.RUNNING.value),
        ("bulk_job_running_response_without_id", ShopifyBulkJobStatus.RUNNING.value),
    ],
    ids=[
        "created",
        "running",
        "running_no_id (edge)",
    ],
)
def test_job_check_with_running_scenario(request, requests_mock, job_response, auth_config, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # modify the sleep time for the test
    stream.job_manager._job_check_interval = 0
    # get job_id from FIXTURE
    job_id = request.getfixturevalue(job_response).get("data", {}).get("node", {}).get("id")
    # mocking the response for STATUS CHECKS
    requests_mock.post(stream.job_manager.base_url, json=request.getfixturevalue(job_response))
    test_job_status_response = requests.post(stream.job_manager.base_url)
    job_result_url = test_job_status_response.json().get("data", {}).get("node", {}).get("url")
    # test the state of the job isn't assigned
    assert stream.job_manager._job_state == None

    # mocking the nested request call to retrieve the data from result URL
    stream.job_manager._job_id = job_id
    requests_mock.get(job_result_url, json=request.getfixturevalue(job_response))

    # calling the sceario processing
    stream.job_manager._job_track_running()
    assert stream.job_manager._job_state == expected


@pytest.mark.parametrize(
    "running_job_response, canceled_job_response, expected",
    [
        (
            "bulk_job_running_with_object_count_and_url_response",
            "bulk_job_canceled_with_object_count_and_url_response",
            "bulk-123456789.jsonl",
        ),
        (
            "bulk_job_running_with_object_count_no_url_response",
            "bulk_job_canceled_with_object_count_no_url_response",
            None,
        ),
    ],
    ids=[
        "self-canceled with url",
        "self-canceled with no url",
    ],
)
def test_job_running_with_canceled_scenario(
    mocker, request, requests_mock, running_job_response, canceled_job_response, auth_config, expected
) -> None:
    stream = MetafieldOrders(auth_config)
    # modify the sleep time for the test
    stream.job_manager._job_check_interval = 0
    # get job_id from FIXTURE
    job_id = request.getfixturevalue(running_job_response).get("data", {}).get("node", {}).get("id")
    # mocking the response for STATUS CHECKS
    requests_mock.post(
        stream.job_manager.base_url,
        [
            {"json": request.getfixturevalue(running_job_response)},
            {"json": request.getfixturevalue(canceled_job_response)},
        ],
    )
    job_result_url = request.getfixturevalue(canceled_job_response).get("data", {}).get("node", {}).get("url")
    # test the state of the job isn't assigned
    assert stream.job_manager._job_state == None

    stream.job_manager._job_id = job_id
    stream.job_manager._job_checkpoint_interval = 5
    # faking self-canceled job
    stream.job_manager._job_self_canceled = True
    # mocking the nested request call to retrieve the data from result URL
    requests_mock.get(job_result_url, json=request.getfixturevalue(canceled_job_response))
    mocker.patch("source_shopify.shopify_graphql.bulk.record.ShopifyBulkRecord.read_file", return_value=[])
    stream.job_manager._job_check_state()
    assert stream.job_manager._job_result_filename == expected
    # clean up
    if expected:
        remove(expected)


def test_job_read_file_invalid_filename(mocker, auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    expected = "An error occured while producing records from BULK Job result"
    # patching the method to get the filename
    mocker.patch("source_shopify.shopify_graphql.bulk.record.ShopifyBulkRecord.produce_records", side_effect=Exception)
    with pytest.raises(ShopifyBulkExceptions.BulkRecordProduceError) as error:
        list(stream.job_manager.record_producer.read_file("test.jsonl"))

    assert expected in repr(error.value)


@pytest.mark.parametrize(
    "stream, json_content_example, expected",
    [
        (CustomerAddress, "customer_address_jsonl_content_example", "customer_address_parse_response_expected_result"),
        (CustomerJourneySummary, "customer_journey_jsonl_content_example", "customer_journey_parse_response_expected_result"),
        (MetafieldOrders, "metafield_jsonl_content_example", "metafield_parse_response_expected_result"),
        (FulfillmentOrders, "filfillment_order_jsonl_content_example", "fulfillment_orders_response_expected_result"),
        (DiscountCodes, "discount_codes_jsonl_content_example", "discount_codes_response_expected_result"),
        (Collections, "collections_jsonl_content_example", "collections_response_expected_result"),
        (TransactionsGraphql, "transactions_jsonl_content_example", "transactions_response_expected_result"),
        (InventoryItems, "inventory_items_jsonl_content_example", "inventory_items_response_expected_result"),
        (InventoryLevels, "inventory_levels_jsonl_content_example", "inventory_levels_response_expected_result"),
        (OrderRisks, "order_risks_jsonl_content_example", "order_risks_response_expected_result"),
        (Products, "products_jsonl_content_example", "products_response_expected_result"),
        (ProductImages, "product_images_jsonl_content_example", "product_images_response_expected_result"),
        (ProductVariants, "product_variants_jsonl_content_example", "product_variants_response_expected_result"),
    ],
    ids=[
        "CustomerAddress",
        "CustomerJourneySummary",
        "MetafieldOrders",
        "FulfillmentOrders",
        "DiscountCodes",
        "Collections",
        "TransactionsGraphql",
        "InventoryItems",
        "InventoryLevels",
        "OrderRisks",
        "Products",
        "ProductImages",
        "ProductVariants",
    ],
)
def test_bulk_stream_parse_response(
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
    # mocking the result url with jsonl content
    requests_mock.post(stream.job_manager.base_url, json=bulk_job_completed_response)
    # mocking nested api call to get data from result url
    requests_mock.get(test_result_url, text=request.getfixturevalue(json_content_example))
    # parsing result from completed job
    test_records = list(stream.read_records(SyncMode.full_refresh, stream_slice={}))
    expected_result = request.getfixturevalue(expected)
    if isinstance(expected_result, dict):
        assert test_records == [expected_result]
    elif isinstance(expected_result, list):
        assert test_records == expected_result


@pytest.mark.parametrize(
    "stream, stream_state, with_start_date, expected_start",
    [
        (DiscountCodes, {}, True, "2023-01-01T00:00:00+00:00"),
        # here the config migration is applied and the value should be "2020-01-01"
        (DiscountCodes, {}, False, "2020-01-01T00:00:00+00:00"),
        (DiscountCodes, {"updated_at": "2022-01-01T00:00:00Z"}, True, "2022-01-01T00:00:00+00:00"),
        (DiscountCodes, {"updated_at": "2021-01-01T00:00:00Z"}, False, "2021-01-01T00:00:00+00:00"),
    ],
    ids=[
        "No State, but Start Date",
        "No State, No Start Date - should fallback to 2018",
        "With State, Start Date",
        "With State, No Start Date",
    ],
)
def test_stream_slices(
    auth_config,
    stream,
    stream_state,
    with_start_date,
    expected_start,
) -> None:
    # simulating `None` for `start_date` and `config migration`
    if not with_start_date:
        auth_config["start_date"] = "2020-01-01"

    stream = stream(auth_config)
    stream.job_manager._job_size = 1000
    test_result = list(stream.stream_slices(stream_state=stream_state))
    assert test_result[0].get("start") == expected_start


@pytest.mark.parametrize(
    "stream, json_content_example, last_job_elapsed_time, previous_slice_size, adjusted_slice_size",
    [
        (CustomerAddress, "customer_address_jsonl_content_example", 20, 4, 5.5),
    ],
    ids=[
        "Expand Slice Size",
    ],
)
def test_expand_stream_slices_job_size(
    request,
    requests_mock,
    bulk_job_completed_response,
    stream,
    json_content_example,
    last_job_elapsed_time,
    previous_slice_size,
    adjusted_slice_size,
    auth_config,
) -> None:
    stream = stream(auth_config)
    # get the mocked job_result_url
    test_result_url = bulk_job_completed_response.get("data").get("node").get("url")
    # mocking the result url with jsonl content
    requests_mock.post(stream.job_manager.base_url, json=bulk_job_completed_response)
    # mocking nested api call to get data from result url
    requests_mock.get(test_result_url, text=request.getfixturevalue(json_content_example))

    # for the sake of simplicity we fake some parts to simulate the `current_job_time_elapsed`
    # fake current slice interval value
    stream.job_manager._job_size = previous_slice_size
    # fake `last job elapsed time`
    if last_job_elapsed_time:
        stream.job_manager._job_last_elapsed_time = last_job_elapsed_time

    first_slice = next(stream.stream_slices())
    list(stream.read_records(SyncMode.incremental, stream_slice=first_slice))
    # check the next slice
    assert stream.job_manager._job_size == adjusted_slice_size
