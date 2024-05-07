#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import requests

from source_shopify import SourceShopify
from source_shopify.shopify_graphql.bulk.exceptions import ShopifyBulkExceptions
from source_shopify.shopify_graphql.bulk.status import ShopifyBulkJobStatus
from source_shopify.streams.streams import (
    Collections,
    CustomerAddress,
    DiscountCodes,
    FulfillmentOrders,
    InventoryItems,
    InventoryLevels,
    MetafieldOrders,
    TransactionsGraphql,
)
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http import HttpResponse
from freezegun import freeze_time
from airbyte_protocol.models import (
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    SyncMode,
)
from typing import Any, Dict, List, Optional
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest


@pytest.mark.parametrize(
    "bulk_job_response, expected_len",
    [
        ("bulk_error", 1),
        ("bulk_unknown_error", 1),
        ("bulk_no_errors", 0),
    ],
)
def test_check_for_errors(request, requests_mock, bulk_job_response, expected_len, auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    requests_mock.get(stream.job_manager.base_url, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.job_manager.base_url)
    test_errors = stream.job_manager._job_check_for_errors(test_response)
    assert len(test_errors) == expected_len


def _catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _read(
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[List[AirbyteStateMessage]] = None,
        expecting_exception: bool = False
) -> EntrypointOutput:
    config = {
        "start_date": "2024-05-05",
        "shop": "airbyte-integration-test",
        "credentials": {
            "auth_method": "api_password",
            "api_password": "api_password",
        },
        "bulk_window_in_days": 1000
    }

    return read(SourceShopify(), config, catalog, state, expecting_exception)


def _scopes_request() -> HttpRequest:
    return HttpRequest(
        url="https://airbyte-integration-test.myshopify.com/admin/oauth/access_scopes.json",
        query_params=ANY_QUERY_PARAMS,
    )


def _shop_request() -> HttpRequest:
    return HttpRequest(
        url="https://airbyte-integration-test.myshopify.com/admin/api/2023-07/shop.json",
        query_params=ANY_QUERY_PARAMS,
    )


def _data_graphql_request() -> HttpRequest:
    return HttpRequest(
        url="https://airbyte-integration-test.myshopify.com/admin/api/2023-07/graphql.json",
        body='{"query": "mutation {\\n                bulkOperationRunQuery(\\n                    query: \\"\\"\\"\\n                     {\\n  orders(\\n    query: \\"updated_at:>=\'2024-05-05T00:00:00+00:00\' AND updated_at:<=\'2024-05-05T02:24:00+00:00\'\\"\\n    sortKey: UPDATED_AT\\n  ) {\\n    edges {\\n      node {\\n        __typename\\n        id\\n        metafields {\\n          edges {\\n            node {\\n              __typename\\n              id\\n              namespace\\n              value\\n              key\\n              description\\n              createdAt\\n              updatedAt\\n              type\\n            }\\n          }\\n        }\\n      }\\n    }\\n  }\\n}\\n                    \\"\\"\\"\\n                ) {\\n                    bulkOperation {\\n                        id\\n                        status\\n                        createdAt\\n                    }\\n                    userErrors {\\n                        field\\n                        message\\n                    }\\n                }\\n            }"}'
    )


def _status_graphql_request() -> HttpRequest:
    return HttpRequest(
        url="https://airbyte-integration-test.myshopify.com/admin/api/2023-07/graphql.json",
        body="""query {
                    node(id: "gid://shopify/BulkOperation/4472588009661") {
                        ... on BulkOperation {
                            id
                            status
                            errorCode
                            createdAt
                            objectCount
                            fileSize
                            url
                            partialDataUrl
                        }
                    }
                }"""
    )


def _records_file_request() -> HttpRequest:
    return HttpRequest(
        url="https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/l6lersgk4i81iqc3n6iisywwtipb-final",
        query_params=ANY_QUERY_PARAMS,
    )


def _register_successful_read_requests(http_mocker: HttpMocker):
    response_scopes = '{"access_scopes":[{"handle":"read_analytics"},{"handle":"read_customers"},{"handle":"read_gdpr_data_request"},{"handle":"read_online_store_navigation"},{"handle":"read_shopify_payments_accounts"},{"handle":"read_shopify_payments_bank_accounts"},{"handle":"read_shopify_payments_disputes"},{"handle":"read_shopify_payments_payouts"},{"handle":"read_assigned_fulfillment_orders"},{"handle":"read_discounts"},{"handle":"read_draft_orders"},{"handle":"read_files"},{"handle":"read_fulfillments"},{"handle":"read_gift_cards"},{"handle":"read_inventory"},{"handle":"read_legal_policies"},{"handle":"read_locations"},{"handle":"read_marketing_events"},{"handle":"read_merchant_managed_fulfillment_orders"},{"handle":"read_online_store_pages"},{"handle":"read_order_edits"},{"handle":"read_orders"},{"handle":"read_price_rules"},{"handle":"read_product_listings"},{"handle":"read_reports"},{"handle":"read_resource_feedbacks"},{"handle":"read_script_tags"},{"handle":"read_shipping"},{"handle":"read_locales"},{"handle":"read_content"},{"handle":"read_themes"},{"handle":"read_third_party_fulfillment_orders"},{"handle":"read_translations"},{"handle":"read_publications"},{"handle":"read_returns"},{"handle":"read_channels"},{"handle":"read_products"},{"handle":"read_markets"},{"handle":"read_shopify_credit"},{"handle":"read_store_credit_account_transactions"},{"handle":"read_all_cart_transforms"},{"handle":"read_cart_transforms"},{"handle":"read_all_checkout_completion_target_customizations"},{"handle":"read_companies"},{"handle":"read_custom_fulfillment_services"},{"handle":"read_customer_data_erasure"},{"handle":"read_customer_merge"},{"handle":"read_dery_customizations"},{"handle":"read_fulfillment_constraint_rules"},{"handle":"read_gates"},{"handle":"read_order_submission_rules"},{"handle":"read_payment_customizations"},{"handle":"read_packing_slip_templates"},{"handle":"read_payment_terms"},{"handle":"read_pixels"},{"handle":"read_product_feeds"},{"handle":"read_purchase_options"},{"handle":"read_shopify_payments_provider_accounts_sensitive"},{"handle":"read_all_orders"}]}'
    response_shop = '{"shop":{"id":58033176765,"name":"airbyte integration test","email":"sherif@airbyte.io","domain":"airbyte-integration-test.myshopify.com","province":"California","country":"US","address1":"350 29th Avenue","zip":"94121","city":"San Francisco","source":null,"phone":"8023494963","latitude":37.7827286,"longitude":-122.4889911,"primary_locale":"en","address2":"","created_at":"2021-06-22T18:00:23-07:00","updated_at":"2024-01-30T21:11:05-08:00","country_code":"US","country_name":"United States","currency":"USD","customer_email":"sherif@airbyte.io","timezone":"(GMT-08:00) America\/Los_Angeles","iana_timezone":"America\/Los_Angeles","shop_owner":"Airbyte Airbyte","money_format":"${{amount}}","money_with_currency_format":"${{amount}} USD","weight_unit":"kg","province_code":"CA","taxes_included":true,"auto_configure_tax_inclusivity":null,"tax_shipping":null,"county_taxes":true,"plan_display_name":"Developer Preview","plan_name":"partner_test","has_discounts":true,"has_gift_cards":false,"myshopify_domain":"airbyte-integration-test.myshopify.com","google_apps_domain":null,"google_apps_login_enabled":null,"money_in_emails_format":"${{amount}}","money_with_currency_in_emails_format":"${{amount}} USD","eligible_for_payments":true,"requires_extra_payments_agreement":false,"password_enabled":true,"has_storefront":true,"finances":true,"primary_location_id":63590301885,"checkout_api_supported":true,"multi_location_enabled":true,"setup_required":false,"pre_launch_enabled":false,"enabled_presentment_currencies":["USD"],"transactional_sms_disabled":false,"marketing_sms_consent_enabled_at_checkout":false}}'
    response_graphql = '{"data":{"bulkOperationRunQuery":{"bulkOperation":{"id":"gid://shopify/BulkOperation/4472588009661","status":"CREATED","createdAt":"2024-05-05T15:34:08Z"},"userErrors":[]}},"extensions":{"cost":{"requestedQueryCost":10,"actualQueryCost":10,"throttleStatus":{"maximumAvailable":2000.0,"currentlyAvailable":1990,"restoreRate":100.0}}}}'
    response_graphql2 = '{"data":{"node":{"id":"gid://shopify/BulkOperation/4476008693949","status":"COMPLETED","errorCode":null,"createdAt":"2024-05-06T20:45:48Z","objectCount":"4","fileSize":"774","url":"https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/l6lersgk4i81iqc3n6iisywwtipb-final?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1715633149&Signature=oMjQelfAzUW%2FdulC3HbuBapbUriUJ%2Bc9%2FKpIIf954VTxBqKChJAdoTmWT9ymh%2FnCiHdM%2BeM%2FADz5siAC%2BXtHBWkJfvs%2F0cYpse0ueiQsw6R8gW5JpeSbizyGWcBBWkv5j8GncAnZOUVYDxRIgfxcPb8BlFxBfC3wsx%2F00v9D6EHbPpkIMTbCOAhheJdw9GmVa%2BOMqHGHlmiADM34RDeBPrvSo65f%2FakpV2LBQTEV%2BhDt0ndaREQ0MrpNwhKnc3vZPzA%2BliOGM0wyiYr9qVwByynHq8c%2FaJPPgI5eGEfQcyepgWZTRW5S0DbmBIFxZJLN6Nq6bJ2bIZWrVriUhNGx2g%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693949.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4476008693949.jsonl&response-content-type=application%2Fjsonl","partialDataUrl":null}},"extensions":{"cost":{"requestedQueryCost":1,"actualQueryCost":1,"throttleStatus":{"maximumAvailable":2000.0,"currentlyAvailable":1999,"restoreRate":100.0}}}}'
    response_data = """{"__typename":"Order","id":"gid:\/\/shopify\/Order\/5010584895677"}
{"__typename":"Metafield","id":"gid:\/\/shopify\/Metafield\/22347288150205","namespace":"my_fields","value":"asdfasdf","key":"purchase_order","description":null,"createdAt":"2023-04-13T12:09:50Z","updatedAt":"2024-05-13T00:09:50Z","type":"single_line_text_field","__parentId":"gid:\/\/shopify\/Order\/5010584895677"}
{"__typename":"Order","id":"gid:\/\/shopify\/Order\/5010585911485"}
{"__typename":"Metafield","id":"gid:\/\/shopify\/Metafield\/22347288740029","namespace":"my_fields","value":"asdfasdfasdf","key":"purchase_order","description":null,"createdAt":"2023-04-13T12:11:20Z","updatedAt":"2024-05-05T00:11:20Z","type":"single_line_text_field","__parentId":"gid:\/\/shopify\/Order\/5010585911485"}
"""

    http_mocker.get(
        _shop_request(),
        HttpResponse(response_shop)
    )
    http_mocker.get(
        _scopes_request(),
        HttpResponse(response_scopes)
    )
    http_mocker.post(
        _data_graphql_request(),
        HttpResponse(response_graphql)
    )
    http_mocker.post(
        _status_graphql_request(),
        HttpResponse(response_graphql2)
    )
    http_mocker.get(
        _records_file_request(),
        HttpResponse(response_data)
    )


# @freeze_time("2024-05-05T01:00:00")
def test_read_graphql_records_successfully():
    with HttpMocker() as http_mocker:
        catalog = _catalog("metafield_orders", SyncMode.full_refresh)

        _register_successful_read_requests(http_mocker)

        output = _read(catalog)

        assert output.records


def test_check_for_errors_with_connection_error() -> None:
    with (HttpMocker() as http_mocker):
        catalog = _catalog("metafield_orders", SyncMode.full_refresh)

        inner_mocker = http_mocker.__getattribute__("_mocker")
        inner_mocker.register_uri("GET", "https://airbyte-integration-test.myshopify.com/admin/api/2023-07/shop.json", exc=ConnectionAbortedError)

        _register_successful_read_requests(http_mocker)

        # TODO: how to check for retries?
        output = _read(catalog)

        print(f"Call Count: {inner_mocker.call_count}")
        print(f"iscalled: {inner_mocker.called}")
        print(f"Mocker history: {inner_mocker.request_history}")
        print(output.errors)
        # assert "ConnectionAbortedError" in output.errors.__str__()
        assert output.records


def test_get_errors_from_response_invalid_response(auth_config) -> None:
    expected = "Couldn't check the `response` for `errors`"
    stream = MetafieldOrders(auth_config)
    response = requests.Response()
    response.status_code = 404
    response.url = "https://example.com/invalid"
    with pytest.raises(ShopifyBulkExceptions.BulkJobBadResponse) as error:
        stream.job_manager._job_check_for_errors(response)
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
    requests_mock.get(stream.job_manager.base_url, json=request.getfixturevalue(bulk_job_response))
    test_response = requests.get(stream.job_manager.base_url)
    test_errors = stream.job_manager._job_check_for_errors(test_response)
    assert stream.job_manager._has_running_concurrent_job(test_errors) == expected


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
    stream.job_manager.job_process_created(test_response)
    assert stream.job_manager._job_id == expected


def test_job_state_completed(auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    stream.job_manager._job_state = ShopifyBulkJobStatus.COMPLETED.value
    assert stream.job_manager._job_completed() == True


@pytest.mark.parametrize(
    "bulk_job_response, concurrent_max_retry, error_type, expected",
    [
        # method should return this response fixture, once retried.
        ("bulk_successful_completed_response", 2, None, "gid://shopify/BulkOperation/4046733967549"),
        # method should raise AirbyteTracebackException, because the concurrent BULK Job is in progress
        (
            "bulk_error_with_concurrent_job", 
            1, 
            ShopifyBulkExceptions.BulkJobConcurrentError, 
            "The BULK Job couldn't be created at this time, since another job is running",
        ),
    ],
    ids=[
        "regular concurrent request",
        "max atttempt reached",
    ]
)
def test_job_retry_on_concurrency(request, requests_mock, bulk_job_response, concurrent_max_retry, error_type, auth_config, expected) -> None:
    stream = MetafieldOrders(auth_config)
    # patching concurent settings
    stream.job_manager._concurrent_max_retry = concurrent_max_retry
    stream.job_manager._concurrent_interval = 1
    
    requests_mock.get(stream.job_manager.base_url, json=request.getfixturevalue(bulk_job_response))
    stream.job_manager._request = requests.get(stream.job_manager.base_url).request
    
    if error_type:
        with pytest.raises(error_type) as error:
            stream.job_manager._job_retry_on_concurrency()
        assert expected in repr(error.value) and requests_mock.call_count == 2
    else:
        # simulate the real job_id from created job
        stream.job_manager._job_id = expected
        stream.job_manager._job_retry_on_concurrency()
        assert requests_mock.call_count == 2


@pytest.mark.parametrize(
    "job_response, error_type, expected",
    [
        ("bulk_job_completed_response", None, "bulk-123456789.jsonl"),
        ("bulk_job_failed_response", ShopifyBulkExceptions.BulkJobFailed, "exited with FAILED"),
        ("bulk_job_timeout_response", ShopifyBulkExceptions.BulkJobTimout, "exited with TIMEOUT"),
        ("bulk_job_access_denied_response", ShopifyBulkExceptions.BulkJobAccessDenied, "exited with ACCESS_DENIED"),
    ],
    ids=[
        "completed",
        "failed",
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
    job_result_url = test_job_status_response.json().get("data", {}).get("node", {}).get("url")
    if error_type:
        with pytest.raises(error_type) as error:
            stream.job_manager.job_check_for_completion()
        assert expected in repr(error.value)
    else:
        if job_result_url:
            # mocking the nested request call to retrieve the data from result URL
            requests_mock.get(job_result_url, json=request.getfixturevalue(job_response))
        result = stream.job_manager.job_check_for_completion()
        assert expected == result

    
@pytest.mark.parametrize(
    "job_response, error_type, max_retry, expected_msg, call_count_expected",
    [
        (
            "bulk_successful_response_with_errors", 
            ShopifyBulkExceptions.BulkJobUnknownError,
            2,
            "Could not validate the status of the BULK Job",
            3,
        ),
        (
            None,
            ShopifyBulkExceptions.BulkJobBadResponse,
            1,
            "Couldn't check the `response` for `errors`",
            2,
        ),
    ],
    ids=[
        "BulkJobUnknownError",
        "BulkJobBadResponse",
    ],
)
def test_retry_on_job_exception(mocker, request, requests_mock, job_response, auth_config, error_type, max_retry, call_count_expected, expected_msg) -> None:
    stream = MetafieldOrders(auth_config)
    stream.job_manager._job_backoff_time = 0
    stream.job_manager._job_max_retries = max_retry
    # patching the method to get the right ID checks
    if job_response:
        stream.job_manager._job_id = request.getfixturevalue(job_response).get("data", {}).get("node", {}).get("id")
        
    # mocking the response for STATUS CHECKS
    json_mock_response = request.getfixturevalue(job_response) if job_response else None
    requests_mock.post(stream.job_manager.base_url, json=json_mock_response)
    
    # testing raised exception and backoff
    with pytest.raises(error_type) as error:
        stream.job_manager._job_check_state()
        
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



def test_job_read_file_invalid_filename(mocker, auth_config) -> None:
    stream = MetafieldOrders(auth_config)
    expected = "An error occured while producing records from BULK Job result"
    # patching the method to get the filename
    mocker.patch("source_shopify.shopify_graphql.bulk.record.ShopifyBulkRecord.produce_records", side_effect=Exception)
    with pytest.raises(ShopifyBulkExceptions.BulkRecordProduceError) as error:
        list(stream.record_producer.read_file("test.jsonl"))

    assert expected in repr(error.value)


@pytest.mark.parametrize(
    "stream, json_content_example, expected",
    [
        (CustomerAddress, "customer_address_jsonl_content_example", "customer_address_parse_response_expected_result"),
        (MetafieldOrders, "metafield_jsonl_content_example", "metafield_parse_response_expected_result"),
        (FulfillmentOrders, "filfillment_order_jsonl_content_example", "fulfillment_orders_response_expected_result"),
        (DiscountCodes, "discount_codes_jsonl_content_example", "discount_codes_response_expected_result"),
        (Collections, "collections_jsonl_content_example", "collections_response_expected_result"),
        (TransactionsGraphql, "transactions_jsonl_content_example", "transactions_response_expected_result"),
        (InventoryItems, "inventory_items_jsonl_content_example", "inventory_items_response_expected_result"),
        (InventoryLevels, "inventory_levels_jsonl_content_example", "inventory_levels_response_expected_result"),
    ],
    ids=[
        "CustomerAddress",
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
    # getting mock response
    test_bulk_response: requests.Response = requests.post(stream.job_manager.base_url)
    # mocking nested api call to get data from result url
    requests_mock.get(test_result_url, text=request.getfixturevalue(json_content_example))
    # parsing result from completed job
    test_records = list(stream.parse_response(test_bulk_response))
    expected_result = request.getfixturevalue(expected)
    if isinstance(expected_result, dict):
        assert test_records == [expected_result]
    elif isinstance(expected_result, list):
        assert test_records == expected_result


@pytest.mark.parametrize(
    "stream, stream_state, with_start_date, expected",
    [
        (DiscountCodes, {}, True, "updated_at:>='2023-01-01T00:00:00+00:00'"),
        # here the config migration is applied and the value should be "2020-01-01"
        (DiscountCodes, {}, False, "updated_at:>='2020-01-01T00:00:00+00:00'"),
        (DiscountCodes, {"updated_at": "2022-01-01T00:00:00Z"}, True, "updated_at:>='2022-01-01T00:00:00+00:00'"),
        (DiscountCodes, {"updated_at": "2021-01-01T00:00:00Z"}, False, "updated_at:>='2021-01-01T00:00:00+00:00'"),
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
    expected, 
) -> None:
    # simulating `None` for `start_date` and `config migration`
    if not with_start_date:
        auth_config["start_date"] = "2020-01-01"

    stream = stream(auth_config)
    stream.job_manager._job_size = 1000
    test_result = list(stream.stream_slices(stream_state=stream_state))
    test_query_from_slice = test_result[0].get("query")
    assert expected in test_query_from_slice

    
@pytest.mark.parametrize(
    "stream, json_content_example, last_job_elapsed_time, previous_slice_size, adjusted_slice_size",
    [
        (CustomerAddress, "customer_address_jsonl_content_example", 10, 4, 5.5),
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
    # getting mock response
    test_bulk_response: requests.Response = requests.post(stream.job_manager.base_url)
    # mocking nested api call to get data from result url
    requests_mock.get(test_result_url, text=request.getfixturevalue(json_content_example))

    # for the sake of simplicity we fake some parts to simulate the `current_job_time_elapsed`
    # fake current slice interval value
    stream.job_manager._job_size = previous_slice_size
    # fake `last job elapsed time` 
    if last_job_elapsed_time:
        stream.job_manager._job_last_elapsed_time = last_job_elapsed_time
    # parsing result from completed job
    list(stream.parse_response(test_bulk_response))
    # check the next slice
    assert stream.job_manager._job_size == adjusted_slice_size
