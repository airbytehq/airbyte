#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from json import dumps
from typing import Any, List, Mapping

import pytest
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"

def records_per_slice(parent_records: List[Mapping[str, Any]], state_checkpoint_interval) -> List[int]:
    num_batches = len(parent_records) // state_checkpoint_interval
    if len(parent_records) % state_checkpoint_interval != 0:
        num_batches += 1
    records_per_slice = len(parent_records) // num_batches
    remaining_elements = len(parent_records) % num_batches
    result = [records_per_slice] * (num_batches - remaining_elements) + [records_per_slice + 1] * remaining_elements
    result.reverse()
    return result

@pytest.fixture
def logger():
    return AirbyteLogger()


@pytest.fixture
def basic_config():
    return {"shop": "test_shop", "credentials": {"auth_method": "api_password", "api_password": "api_password"}}


@pytest.fixture
def auth_config():
    return {
        "shop": "test_shop",
        "start_date": "2023-01-01",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "authenticator": None,
    }


@pytest.fixture
def catalog_with_streams():
    def _catalog_with_streams(names):
        streams = []
        for name in names:
            streams.append(
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(name=name, json_schema={"type": "object"}),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            )
        return ConfiguredAirbyteCatalog(streams=streams)

    return _catalog_with_streams


@pytest.fixture
def response_with_bad_json():
    bad_json_str = '{"customers": [{ "field1": "test1", "field2": }]}'
    response = requests.Response()
    response.status_code = 200
    response._content = bad_json_str.encode("utf-8")
    return response


@pytest.fixture
def bulk_error() -> dict[str, Any]:
    return {
        "data": {
            "bulkOperationRunQuery": {
                "bulkOperation": None,
                "userErrors": [
                    {
                        "field": "some_field",
                        "message": "something wrong with the requested field.",
                    },
                ],
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_unknown_error() -> dict[str, Any]:
    return {
        "errors": [
            {
                "message": "something wrong with the job",
            },
        ],
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_no_errors() -> dict[str, Any]:
    return {}


@pytest.fixture
def bulk_error_with_concurrent_job():
    return {
        "data": {
            "bulkOperationRunQuery": {
                "bulkOperation": None,
                "userErrors": [
                    {
                        "field": None,
                        "message": "",
                    },
                    {
                        "field": None,
                        "message": "A bulk query operation for this app and shop is already in progress: gid://shopify/BulkOperation/4046676525245.",
                    },
                ],
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_successful_response():
    return {
        "data": {
            "bulkOperationRunQuery": {
                "bulkOperation": {
                    "id": "gid://shopify/BulkOperation/4046733967549",
                    "status": "CREATED",
                },
                "userErrors": [],
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_successful_response_with_errors():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4046733967549",
                "status": "RUNNING",
            },
            "bulkOperationRunQuery": {
                "userErrors": [
                    {
                        "message": "something wrong with the job",
                    },
                ],
            },
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_successful_response_with_no_id():
    return {
        "data": {
            "bulkOperationRunQuery": {
                "bulkOperation": {
                    "status": "RUNNING",
                },
                "userErrors": [],
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_successful_completed_response():
    return {
        "data": {
            "bulkOperationRunQuery": {
                "bulkOperation": {
                    "id": "gid://shopify/BulkOperation/4046733967549",
                    "status": "CREATED",
                    "url": '"https://some_url/response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8'
                    'bulk-4047416819901.jsonl&response-content-type=application/jsonl"',
                },
                "userErrors": [],
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_created_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4046733967549",
                "status": "CREATED",
                "userErrors": [],
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 10,
                "actualQueryCost": 10,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 990,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_completed_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "COMPLETED",
                "errorCode": None,
                "objectCount": "0",
                "fileSize": None,
                "url": 'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8'
                "bulk-123456789.jsonl&response-content-type=application/jsonl",
                "partialDataUrl": None,
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 999,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_failed_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "FAILED",
                "errorCode": None,
                "objectCount": "0",
                "fileSize": None,
                "url": None,
                "partialDataUrl": None,
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 999,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_timeout_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "TIMEOUT",
                "errorCode": None,
                "objectCount": "0",
                "fileSize": None,
                "url": None,
                "partialDataUrl": None,
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 999,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_running_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "RUNNING",
                "errorCode": None,
                "objectCount": "0",
                "fileSize": None,
                "url": None,
                "partialDataUrl": None,
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 999,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_running_response_without_id():
    return {
        "data": {
            "node": {
                # "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "RUNNING",
                "errorCode": None,
                "objectCount": "0",
                "fileSize": None,
                "url": None,
                "partialDataUrl": None,
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 999,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_access_denied_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "ACCESS_DENIED",
                "errorCode": None,
                "objectCount": "0",
                "fileSize": None,
                "url": None,
                "partialDataUrl": None,
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 999,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def bulk_job_unknown_status_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": None,
                "errorCode": None,
                "objectCount": "0",
                "fileSize": None,
                "url": None,
                "partialDataUrl": None,
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 1000.0,
                    "currentlyAvailable": 999,
                    "restoreRate": 50.0,
                },
            }
        },
    }


@pytest.fixture
def metafield_jsonl_content_example():
    return (
        dumps(
            {
                "__typename": "Metafield",
                "id": "gid://shopify/Metafield/123",
                "__parentId": "gid://shopify/Order/1234567",
                "createdAt": "2023-01-01T01:01:01Z",
                "updatedAt": "2023-01-01T01:01:01Z",
            }
        )
        + "\n"
    )


@pytest.fixture
def filfillment_order_jsonl_content_example():
    return """{"__typename":"Order","id":"gid:\/\/shopify\/Order\/1"}
{"__typename":"FulfillmentOrder","id":"gid:\/\/shopify\/FulfillmentOrder\/2","assignedLocation":{"address1":"Test","address2":null,"city":"Test","countryCode":"Test","name":"Test","phone":"","province":null,"zip":"00000","location":{"locationId":"gid:\/\/shopify\/Location\/123"}},"destination":{"id":"gid:\/\/shopify\/Destination\/777"},"deliveryMethod":{"id":"gid:\/\/shopify\/DeliveryMethod\/123","methodType":"SHIPPING","minDeliveryDateTime":"2023-04-13T12:00:00Z","maxDeliveryDateTime":"2023-04-13T12:00:00Z"},"fulfillAt":"2023-04-13T12:00:00Z","fulfillBy":null,"internationalDuties":null,"fulfillmentHolds":[{}],"createdAt":"2023-04-13T12:09:45Z","updatedAt":"2023-04-13T12:09:46Z","requestStatus":"UNSUBMITTED","status":"CLOSED","supportedActions":[{}],"__parentId":"gid:\/\/shopify\/Order\/1"}
{"__typename":"FulfillmentOrderLineItem","id":"gid:\/\/shopify\/FulfillmentOrderLineItem\/3","inventoryItemId":"gid:\/\/shopify\/InventoryItem\/33","lineItem":{"lineItemId":"gid:\/\/shopify\/LineItem\/31","fulfillableQuantity":0,"quantity":1,"variant":{"variantId":"gid:\/\/shopify\/ProductVariant\/333"}},"__parentId":"gid:\/\/shopify\/FulfillmentOrder\/2"}
{"__typename":"FulfillmentOrderMerchantRequest","id":"gid:\/\/shopify\/FulfillmentOrderMerchantRequest\/333","message":null,"kind":"FULFILLMENT_REQUEST","requestOptions":{"notify_customer":true},"__parentId":"gid:\/\/shopify\/FulfillmentOrder\/2"}\n"""


@pytest.fixture
def inventory_items_jsonl_content_example():
    return """{"__typename":"InventoryItem","id":"gid:\/\/shopify\/InventoryItem\/44871665713341","unitCost":null,"countryCodeOfOrigin":null,"harmonizedSystemCode":null,"provinceCodeOfOrigin":null,"updatedAt":"2023-04-14T10:29:27Z","createdAt":"2023-04-14T10:29:27Z","sku":"","tracked":true,"requiresShipping":false}
{"__typename":"InventoryItem","id":"gid:\/\/shopify\/InventoryItem\/45419395743933","unitCost":{"cost":"29.0"},"countryCodeOfOrigin":"UA","harmonizedSystemCode":"330510","provinceCodeOfOrigin":null,"updatedAt":"2023-12-11T10:37:41Z","createdAt":"2023-12-11T10:37:41Z","sku":"123","tracked":true,"requiresShipping":true}\n"""


@pytest.fixture
def customer_address_jsonl_content_example():
    return """{"__typename":"Customer","id":"gid:\/\/shopify\/Customer\/123","defaultAddress":{"id":"gid:\/\/shopify\/MailingAddress\/123?model_name=CustomerAddress"},"addresses":[{"address1":"My Best Accent","address2":"","city":"Fair Lawn","country":"United States","countryCode":"US","company":"Test Company","firstName":"New Test","id":"gid:\/\/shopify\/MailingAddress\/123?model_name=CustomerAddress","lastName":"Customer","name":"New Test Customer","phone":"","province":"New Jersey","provinceCode":"NJ","zip":"07410"}],"updatedAt":"2023-04-24T13:53:48Z"}
{"__typename":"Customer","id":"gid:\/\/shopify\/Customer\/456","defaultAddress":{"id":"gid:\/\/shopify\/MailingAddress\/456?model_name=CustomerAddress"},"addresses":[{"address1":null,"address2":null,"city":null,"country":null,"countryCode":null,"company":null,"firstName":"MArcos","id":"gid:\/\/shopify\/MailingAddress\/456?model_name=CustomerAddress","lastName":"Millnitz","name":"MArcos Millnitz","phone":null,"province":null,"provinceCode":null,"zip":null}],"updatedAt":"2023-07-11T20:07:45Z"}\n"""


@pytest.fixture
def inventory_levels_jsonl_content_example():
    return """{"__typename":"Location","id":"gid:\/\/shopify\/Location\/63590301885"}
{"__typename":"InventoryLevel","id":"gid:\/\/shopify\/InventoryLevel\/97912455357?inventory_item_id=42185200631997","available":15,"item":{"inventory_item_id":"gid:\/\/shopify\/InventoryItem\/42185200631997"},"updatedAt":"2023-04-13T12:00:55Z","__parentId":"gid:\/\/shopify\/Location\/63590301885"}
{"__typename":"InventoryLevel","id":"gid:\/\/shopify\/InventoryLevel\/97912455357?inventory_item_id=42185218719933","available":8,"item":{"inventory_item_id":"gid:\/\/shopify\/InventoryItem\/42185218719933"},"updatedAt":"2023-04-13T12:09:45Z","__parentId":"gid:\/\/shopify\/Location\/63590301885"}\n"""


@pytest.fixture
def discount_codes_jsonl_content_example():
    return """{"__typename":"DiscountCodeNode","id":"gid:\/\/shopify\/DiscountCodeNode\/945205379261","codeDiscount":{"updatedAt":"2023-12-07T11:40:44Z","createdAt":"2021-07-08T12:40:37Z","summary":"Free shipping on all products • Minimum purchase of $1.00 • For all countries","discountType":"SHIPPING"}}
{"__typename":"DiscountRedeemCode","usageCount":0,"code":"TEST","id":"gid:\/\/shopify\/DiscountRedeemCode\/11545139282109","__parentId":"gid:\/\/shopify\/DiscountCodeNode\/945205379261"}
{"__typename":"DiscountRedeemCode","usageCount":0,"code":"TEST2","id":"gid:\/\/shopify\/DiscountRedeemCode\/13175793582269","__parentId":"gid:\/\/shopify\/DiscountCodeNode\/945205379261"}\n"""


@pytest.fixture
def collections_jsonl_content_example():
    return """{"__typename":"Collection","id":"gid:\/\/shopify\/Collection\/270889287869","handle":"frontpage","title":"Home page","updatedAt":"2023-09-05T14:06:59Z","bodyHtml":"updated_mon_24.04.2023","sortOrder":"BEST_SELLING","templateSuffix":"","productsCount":1}
{"__typename":"CollectionPublication","publishedAt":"2021-06-23T01:00:25Z","__parentId":"gid:\/\/shopify\/Collection\/270889287869"}
{"__typename":"CollectionPublication","publishedAt":"2021-08-18T09:39:34Z","__parentId":"gid:\/\/shopify\/Collection\/270889287869"}
{"__typename":"CollectionPublication","publishedAt":"2023-04-20T11:12:24Z","__parentId":"gid:\/\/shopify\/Collection\/270889287869"}
{"__typename":"Collection","id":"gid:\/\/shopify\/Collection\/273278566589","handle":"test-collection","title":"Test Collection","updatedAt":"2023-09-05T14:12:04Z","bodyHtml":"updated_mon_24.04.2023","sortOrder":"BEST_SELLING","templateSuffix":"","productsCount":26}
{"__typename":"CollectionPublication","publishedAt":"2021-07-19T14:02:54Z","__parentId":"gid:\/\/shopify\/Collection\/273278566589"}
{"__typename":"CollectionPublication","publishedAt":"2021-08-18T09:39:34Z","__parentId":"gid:\/\/shopify\/Collection\/273278566589"}
{"__typename":"CollectionPublication","publishedAt":"2023-04-20T11:12:24Z","__parentId":"gid:\/\/shopify\/Collection\/273278566589"}\n"""


@pytest.fixture
def transactions_jsonl_content_example():
    return (
        dumps(
            {
                "__typename": "Order",
                "id": "gid://shopify/Order/1",
                "currency": "USD",
                "transactions": [
                    {
                        "id": "gid://shopify/OrderTransaction/1",
                        "errorCode": None,
                        "parentTransaction": {"parentId": "gid://shopify/ParentOrderTransaction/0"},
                        "test": True,
                        "kind": "SALE",
                        "amount": "102.00",
                        "receipt": '{"paid_amount":"102.00"}',
                        "gateway": "test",
                        "authorization": "1234",
                        "createdAt": "2030-07-02T07:51:49Z",
                        "status": "SUCCESS",
                        "processedAt": "2030-07-02T07:51:49Z",
                        "totalUnsettledSet": {
                            "presentmentMoney": {"amount": "0.0", "currency": "USD"},
                            "shopMoney": {"amount": "0.0", "currency": "USD"},
                        },
                        "paymentId": "some_payment_id.1",
                        "paymentDetails": {
                            "avsResultCode": None,
                            "cvvResultCode": None,
                            "creditCardBin": "1",
                            "creditCardCompany": "Test",
                            "creditCardNumber": "•••• •••• •••• 1",
                            "creditCardName": "Test Gateway",
                            "creditCardWallet": None,
                            "creditCardExpirationYear": 2023,
                            "creditCardExpirationMonth": 11,
                        },
                    }
                ],
            }
        )
        + "\n"
    )


@pytest.fixture
def metafield_parse_response_expected_result():
    return {
        "id": 123,
        "admin_graphql_api_id": "gid://shopify/Metafield/123",
        "owner_id": 1234567,
        "owner_resource": "order",
        "shop_url": "test_shop",
        "created_at": "2023-01-01T01:01:01+00:00",
        "updated_at": "2023-01-01T01:01:01+00:00",
    }


@pytest.fixture
def fulfillment_orders_response_expected_result():
    return {
        "id": 2,
        "assigned_location": {
            "address1": "Test",
            "address2": None,
            "city": "Test",
            "country_code": "Test",
            "name": "Test",
            "phone": "",
            "province": None,
            "zip": "00000",
            "location_id": 123,
        },
        "destination": {
            "id": 777,
        },
        "delivery_method": {
            "id": 123,
            "method_type": "SHIPPING",
            "min_delivery_date_time": "2023-04-13T12:00:00+00:00",
            "max_delivery_date_time": "2023-04-13T12:00:00+00:00",
        },
        "fulfill_at": "2023-04-13T12:00:00+00:00",
        "fulfill_by": None,
        "international_duties": None,
        "fulfillment_holds": [],
        "created_at": "2023-04-13T12:09:45+00:00",
        "updated_at": "2023-04-13T12:09:46+00:00",
        "request_status": "UNSUBMITTED",
        "status": "CLOSED",
        "supported_actions": [],
        "shop_id": None,
        "order_id": 1,
        "assigned_location_id": 123,
        "line_items": [
            {
                "id": 3,
                "inventory_item_id": 33,
                "shop_id": None,
                "fulfillment_order_id": 2,
                "quantity": 1,
                "line_item_id": 31,
                "fulfillable_quantity": 0,
                "variant_id": 333,
            },
        ],
        "merchant_requests": [{"id": 333, "message": None, "kind": "FULFILLMENT_REQUEST", "request_options": {"notify_customer": True}}],
        "admin_graphql_api_id": "gid://shopify/FulfillmentOrder/2",
        "shop_url": "test_shop",
    }


@pytest.fixture
def inventory_items_response_expected_result():
    return [
        {
            "id": 44871665713341,
            "country_code_of_origin": None,
            "harmonized_system_code": None,
            "province_code_of_origin": None,
            "updated_at": "2023-04-14T10:29:27+00:00",
            "created_at": "2023-04-14T10:29:27+00:00",
            "sku": "",
            "tracked": True,
            "requires_shipping": False,
            "admin_graphql_api_id": "gid://shopify/InventoryItem/44871665713341",
            "cost": None,
            "country_harmonized_system_codes": [],
            "shop_url": "test_shop",
        },
        {
            "id": 45419395743933,
            "country_code_of_origin": "UA",
            "harmonized_system_code": "330510",
            "province_code_of_origin": None,
            "updated_at": "2023-12-11T10:37:41+00:00",
            "created_at": "2023-12-11T10:37:41+00:00",
            "sku": "123",
            "tracked": True,
            "requires_shipping": True,
            "admin_graphql_api_id": "gid://shopify/InventoryItem/45419395743933",
            "cost": 29.0,
            "country_harmonized_system_codes": [],
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def customer_address_parse_response_expected_result():
    return [
    {
        "address1": "My Best Accent",
        "address2": "",
        "city": "Fair Lawn",
        "country": "United States",
        "country_code": "US",
        "company": "Test Company",
        "first_name": "New Test",
        "id": 123,
        "last_name": "Customer",
        "name": "New Test Customer",
        "phone": "",
        "province": "New Jersey",
        "province_code": "NJ",
        "zip": "07410",
        "customer_id": 123,
        "country_name": "United States",
        "default": True,
        "updated_at": "2023-04-24T13:53:48+00:00",
        "shop_url": "test_shop"
    },
    {
        "address1": None,
        "address2": None,
        "city": None,
        "country": None,
        "country_code": None,
        "company": None,
        "first_name": "MArcos",
        "id": 456,
        "last_name": "Millnitz",
        "name": "MArcos Millnitz",
        "phone": None,
        "province": None,
        "province_code": None,
        "zip": None,
        "customer_id": 456,
        "country_name": None,
        "default": True,
        "updated_at": "2023-07-11T20:07:45+00:00",
        "shop_url": "test_shop"
    }
]


@pytest.fixture
def inventory_levels_response_expected_result():
    return [
        {
            "id": "63590301885|42185200631997",
            "available": 15,
            "updated_at": "2023-04-13T12:00:55+00:00",
            "admin_graphql_api_id": "gid://shopify/InventoryLevel/97912455357?inventory_item_id=42185200631997",
            "inventory_item_id": 42185200631997,
            "location_id": 63590301885,
            "shop_url": "test_shop",
        },
        {
            "id": "63590301885|42185218719933",
            "available": 8,
            "updated_at": "2023-04-13T12:09:45+00:00",
            "admin_graphql_api_id": "gid://shopify/InventoryLevel/97912455357?inventory_item_id=42185218719933",
            "inventory_item_id": 42185218719933,
            "location_id": 63590301885,
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def discount_codes_response_expected_result():
    return [
        {
            "usage_count": 0,
            "code": "TEST",
            "id": 11545139282109,
            "admin_graphql_api_id": "gid://shopify/DiscountRedeemCode/11545139282109",
            "price_rule_id": 945205379261,
            "updated_at": "2023-12-07T11:40:44+00:00",
            "created_at": "2021-07-08T12:40:37+00:00",
            "summary": "Free shipping on all products • Minimum purchase of $1.00 • For all countries",
            "discount_type": "SHIPPING",
            "shop_url": "test_shop",
        },
        {
            "usage_count": 0,
            "code": "TEST2",
            "id": 13175793582269,
            "admin_graphql_api_id": "gid://shopify/DiscountRedeemCode/13175793582269",
            "price_rule_id": 945205379261,
            "updated_at": "2023-12-07T11:40:44+00:00",
            "created_at": "2021-07-08T12:40:37+00:00",
            "summary": "Free shipping on all products • Minimum purchase of $1.00 • For all countries",
            "discount_type": "SHIPPING",
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def collections_response_expected_result():
    return [
        {
            "id": 270889287869,
            "handle": "frontpage",
            "title": "Home page",
            "updated_at": "2023-09-05T14:06:59+00:00",
            "body_html": "updated_mon_24.04.2023",
            "sort_order": "BEST_SELLING",
            "template_suffix": "",
            "products_count": 1,
            "admin_graphql_api_id": "gid://shopify/Collection/270889287869",
            "published_at": "2021-06-23T01:00:25+00:00",
            "shop_url": "test_shop",
        },
        {
            "id": 273278566589,
            "handle": "test-collection",
            "title": "Test Collection",
            "updated_at": "2023-09-05T14:12:04+00:00",
            "body_html": "updated_mon_24.04.2023",
            "sort_order": "BEST_SELLING",
            "template_suffix": "",
            "products_count": 26,
            "admin_graphql_api_id": "gid://shopify/Collection/273278566589",
            "published_at": "2021-07-19T14:02:54+00:00",
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def transactions_response_expected_result():
    return {
        "id": 1,
        "error_code": None,
        "test": True,
        "kind": "SALE",
        "amount": 102.0,
        "receipt": '{"paid_amount":"102.00"}',
        "gateway": "test",
        "authorization": "1234",
        "created_at": "2030-07-02T07:51:49+00:00",
        "status": "SUCCESS",
        "processed_at": "2030-07-02T07:51:49+00:00",
        "total_unsettled_set": {"presentment_money": {"amount": 0.0, "currency": "USD"}, "shop_money": {"amount": 0.0, "currency": "USD"}},
        "payment_id": "some_payment_id.1",
        "payment_details": {
            "avs_result_code": None,
            "cvv_result_code": None,
            "credit_card_bin": "1",
            "credit_card_company": "Test",
            "credit_card_number": "•••• •••• •••• 1",
            "credit_card_name": "Test Gateway",
            "credit_card_wallet": None,
            "credit_card_expiration_year": 2023,
            "credit_card_expiration_month": 11,
        },
        "order_id": 1,
        "currency": "USD",
        "admin_graphql_api_id": "gid://shopify/OrderTransaction/1",
        "parent_id": 0,
        "shop_url": "test_shop",
    }
