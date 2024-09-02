#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from json import dumps
from typing import Any, List, Mapping

import pytest
import requests
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


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
    return logging.getLogger("airbyte")


@pytest.fixture
def basic_config():
    return {
        "shop": "test_shop", 
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "shop_id": 0,
    }


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
def bulk_job_failed_with_partial_url_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/123",
                "status": "FAILED",
                "errorCode": "INTERNAL_SERVER_ERROR",
                "objectCount": "432",
                "fileSize": None,
                "url": None,
                "partialDataUrl": 'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8'
                "bulk-123456789.jsonl&response-content-type=application/jsonl"
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "actualQueryCost": 1,
                "throttleStatus": {
                    "maximumAvailable": 20000.0,
                    "currentlyAvailable": 19999,
                    "restoreRate": 1000.0
                }
            }
        }
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
def bulk_job_running_with_object_count_and_url_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "RUNNING",
                "errorCode": None,
                "objectCount": "15",
                "fileSize": None,
                "url": 'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8',
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
def bulk_job_canceled_with_object_count_and_url_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "CANCELED",
                "errorCode": None,
                "objectCount": "15",
                "fileSize": None,
                "url": 'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8',
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
def bulk_job_running_with_object_count_no_url_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "RUNNING",
                "errorCode": None,
                "objectCount": "4",
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
def bulk_job_canceled_with_object_count_no_url_response():
    return {
        "data": {
            "node": {
                "id": "gid://shopify/BulkOperation/4047052112061",
                "status": "CANCELED",
                "errorCode": None,
                "objectCount": "4",
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
{"__typename":"FulfillmentOrder","id":"gid:\/\/shopify\/FulfillmentOrder\/2","fulfillAt":"2023-04-24T18:00:00Z","fulfillBy":null,"createdAt":"2023-04-24T18:00:09Z","updatedAt":"2023-04-24T18:00:09Z","requestStatus":"UNSUBMITTED","status":"CLOSED","channelId":null,"assignedLocation":{"address1":"Heroiv UPA 72","address2":null,"city":"Lviv","countryCode":"UA","name":"Heroiv UPA 72","phone":"","province":null,"zip":"30100","location":{"locationId":"gid:\/\/shopify\/Location\/63590301885"}},"destination":null,"deliveryMethod":{"id":"gid:\/\/shopify\/DeliveryMethod\/442031046845","methodType":"SHIPPING","minDeliveryDateTime":null,"maxDeliveryDateTime":null},"internationalDuties":null,"fulfillmentHolds":[],"supportedActions":[],"__parentId":"gid:\/\/shopify\/Order\/1"}
{"__typename":"FulfillmentOrderLineItem","id":"gid:\/\/shopify\/FulfillmentOrderLineItem\/3","inventoryItemId":"gid:\/\/shopify\/InventoryItem\/43653688524989","lineItem":{"lineItemId":"gid:\/\/shopify\/LineItem\/12247585521853","fulfillableQuantity":0,"quantity":1,"variant":{"variantId":"gid:\/\/shopify\/ProductVariant\/41561961824445"}},"__parentId":"gid:\/\/shopify\/FulfillmentOrder\/2"}
{"__typename":"FulfillmentOrderMerchantRequest","id":"gid:\/\/shopify\/FulfillmentOrderMerchantRequest\/333","message":null,"kind":"FULFILLMENT_REQUEST","requestOptions":{"notify_customer":true},"__parentId":"gid:\/\/shopify\/FulfillmentOrder\/2"}\n"""


@pytest.fixture
def order_risks_jsonl_content_example():
    return """{"__typename":"Order","updatedAt":"2023-09-09T09:57:43Z","order_id":"gid:\/\/shopify\/Order\/3944273805501","risk":{"recommendation":"NONE","assessments":[{"risk_level":"NONE","facts":[{"description":"Card Verification Value (CVV) isn't available","sentiment":"NEUTRAL"},{"description":"Billing address or credit card's address wasn't available","sentiment":"NEUTRAL"},{"description":"Billing address ZIP or postal code isn't available to match with credit card's registered address","sentiment":"NEUTRAL"},{"description":"The payment method used isn't available","sentiment":"NEUTRAL"},{"description":"Location of IP address used to place the order isn't available","sentiment":"NEUTRAL"},{"description":"Distance between shipping address and location of IP address isn't available","sentiment":"NEUTRAL"},{"description":"The billing country or the country of the IP used to place the order isn't available","sentiment":"NEUTRAL"},{"description":"Can't determine if a high risk internet connection was used because the IP address isn't available","sentiment":"NEUTRAL"},{"description":"There was 1 payment attempt","sentiment":"POSITIVE"}],"provider":null}]}}
{"__typename":"Order","updatedAt":"2023-09-19T14:29:22Z","order_id":"gid:\/\/shopify\/Order\/3945528492221","risk":{"recommendation":"CANCEL","assessments":[{"risk_level":"NONE","facts":[{"description":"Card Verification Value (CVV) isn't available","sentiment":"NEUTRAL"},{"description":"Billing address or credit card's address wasn't available","sentiment":"NEUTRAL"},{"description":"Billing address ZIP or postal code isn't available to match with credit card's registered address","sentiment":"NEUTRAL"},{"description":"The payment method used isn't available","sentiment":"NEUTRAL"},{"description":"Location of IP address used to place the order isn't available","sentiment":"NEUTRAL"},{"description":"Distance between shipping address and location of IP address isn't available","sentiment":"NEUTRAL"},{"description":"The billing country or the country of the IP used to place the order isn't available","sentiment":"NEUTRAL"},{"description":"Can't determine if a high risk internet connection was used because the IP address isn't available","sentiment":"NEUTRAL"},{"description":"There was 1 payment attempt","sentiment":"POSITIVE"}],"provider":null},{"risk_level":"HIGH","facts":[{"description":"This order came from an anonymous proxy","sentiment":"NEGATIVE"}],"provider":{"features":[],"description":null,"handle":null,"embedded":false,"title":"Airbyte Test","published":false,"developer_name":"app developer","developer_type":"MERCHANT","app_store_app_url":null,"install_url":null,"app_store_developer_url":null,"is_post_purchase_app_in_use":false,"previously_installed":false,"pricing_details_summary":"Free","pricing_details":null,"privacy_policy_url":null,"public_category":"CUSTOM","uninstall_message":"You won't be able to view or access features for this app anymore. Discounts that use this app will also be deleted.","webhook_api_version":"2023-04","shopify_developed":false,"provider_id":"gid:\/\/shopify\/App\/5505221","failed_requirements":[],"feedback":null}}]}}\n"""


@pytest.fixture
def products_jsonl_content_example():
    return """{"__typename":"Product","id":"gid:\/\/shopify\/Product\/123","publishedAt":"2021-06-23T01:09:29Z","createdAt":"2021-06-23T01:09:29Z","status":"ACTIVE","vendor":"Blanda, O'Kon and Bartell","updatedAt":"2023-04-20T11:12:26Z","bodyHtml":"Gold and silver glitter iPhone 7 cases with geometric line patterns, stacked","productType":"Music","tags":["developer-tools-generator"],"handle":"gold-silver-iphone-7-case","templateSuffix":null,"title":"Gold Silver iPhone 7 Case","description":"Gold and silver glitter iPhone 7 cases with geometric line patterns, stacked","descriptionHtml":"Gold and silver glitter iPhone 7 cases with geometric line patterns, stacked","isGiftCard":false,"legacyResourceId":"123","onlineStorePreviewUrl":"https:\/\/airbyte-integration-test.myshopify.com\/products\/gold-silver-iphone-7-case","onlineStoreUrl":null,"totalInventory":58,"tracksInventory":true,"hasOnlyDefaultVariant":false,"hasOutOfStockVariants":false,"requiresSellingPlan":false,"priceRangeV2":{"max_variant_price":{"amount":"99.0","currency_code":"USD"},"min_variant_price":{"amount":"98.0","currency_code":"USD"}},"featuredImage":{"height":3709,"id":"gid:\/\/shopify\/ProductImage\/29301295579325","url":"https:\/\/cdn.shopify.com\/s\/files\/1\/0580\/3317\/6765\/products\/gold-silver-iphone-7-case.jpg?v=1624410569","width":5563,"alt_text":null},"seo":{"description":null,"title":null},"featuredMedia":{"alt":"","id":"gid:\/\/shopify\/MediaImage\/21562154123453","status":"READY","media_content_type":"IMAGE","preview":{"status":"READY","image":{"id":"gid:\/\/shopify\/ImageSource\/21570958426301","alt_text":""}},"media_errors":[],"media_warnings":[]},"feedback":null,"total_variants":{"total_variants":2},"media_count":{"media_count":1},"options":[{"id":"gid:\/\/shopify\/ProductOption\/8720175628477","name":"Title","values":["Plastic","indigo"],"position":1}]}
{"__typename":"Image","id":"gid:\/\/shopify\/ProductImage\/111","__parentId":"gid:\/\/shopify\/Product\/123"}
{"__typename":"ProductVariant","id":"gid:\/\/shopify\/ProductVariant\/111","__parentId":"gid:\/\/shopify\/Product\/123"}
{"__typename":"ProductVariant","id":"gid:\/\/shopify\/ProductVariant\/222","__parentId":"gid:\/\/shopify\/Product\/123"}\n"""


@pytest.fixture
def product_images_jsonl_content_example():
    return """{"__typename":"Product","id":"gid:\/\/shopify\/Product\/123"}
{"__typename":"MediaImage","createdAt":"2023-01-06T18:29:17Z","updatedAt":"2023-01-06T18:29:19Z","image":{"url":"https:\/\/cdn.shopify.com\/s\/files\/1\/0580\/3317\/6765\/products\/white-t-shirt.jpg?v=1673029759"},"__parentId":"gid:\/\/shopify\/Product\/123"}
{"__typename":"Image","id":"gid:\/\/shopify\/ProductImage\/111","height":280,"alt":"","src":"https:\/\/cdn.shopify.com\/s\/files\/1\/0580\/3317\/6765\/products\/white-t-shirt.jpg?v=1673029759","url":"https:\/\/cdn.shopify.com\/s\/files\/1\/0580\/3317\/6765\/products\/white-t-shirt.jpg?v=1673029759","width":265,"__parentId":"gid:\/\/shopify\/Product\/123"}
{"__typename":"Product","id":"gid:\/\/shopify\/Product\/456"}
{"__typename":"MediaImage","createdAt":"2021-06-23T01:09:47Z","updatedAt":"2023-04-24T17:27:15Z","image":{"url":"https:\/\/cdn.shopify.com\/s\/files\/1\/0580\/3317\/6765\/products\/4-ounce-soy-candle.jpg?v=1624410587"},"__parentId":"gid:\/\/shopify\/Product\/456"}
{"__typename":"Image","id":"gid:\/\/shopify\/ProductImage\/222","height":1467,"alt":"updated_mon_24.04.2023","src":"https:\/\/cdn.shopify.com\/s\/files\/1\/0580\/3317\/6765\/products\/4-ounce-soy-candle.jpg?v=1624410587","url":"https:\/\/cdn.shopify.com\/s\/files\/1\/0580\/3317\/6765\/products\/4-ounce-soy-candle.jpg?v=1624410587","width":2200,"__parentId":"gid:\/\/shopify\/Product\/456"}
{"__typename":"Product","id":"gid:\/\/shopify\/Product\/9062091161885"}
{"__typename":"MediaImage","createdAt":"2024-06-12T23:41:27Z","updatedAt":"2024-06-12T23:41:28Z","image":null,"__parentId":"gid:\/\/shopify\/Product\/9062091161885"}\n"""


@pytest.fixture
def product_variants_jsonl_content_example():
    return """{"__typename":"ProductVariant","id":"gid:\/\/shopify\/ProductVariant\/40091751448765","title":"Metal","price":"64.00","sku":"","position":1,"inventoryPolicy":"DENY","compareAtPrice":null,"inventoryManagement":"SHOPIFY","createdAt":"2021-06-23T06:04:41Z","updatedAt":"2023-10-27T16:56:50Z","taxable":true,"barcode":null,"weight":0.0,"weightUnit":"GRAMS","inventoryQuantity":6,"requiresShipping":false,"availableForSale":true,"displayName":"Waterproof iPhone Speaker - Metal","taxCode":"","grams":0.0,"image":null,"old_inventory_quantity":6,"product":{"product_id":"gid:\/\/shopify\/Product\/6796825198781"},"fulfillmentService":{"fulfillment_service":"manual"},"inventoryItem":{"inventory_item_id":"gid:\/\/shopify\/InventoryItem\/42186366255293"}}
{"__typename":"ProductVariantPricePair","price":{"amount":"64.0","currencyCode":"USD"},"compareAtPrice":null,"__parentId":"gid:\/\/shopify\/ProductVariant\/40091751448765"}
{"__typename":"ProductVariant","id":"gid:\/\/shopify\/ProductVariant\/41561955827901","title":"Test Variant 1","price":"19.00","sku":"","position":2,"inventoryPolicy":"DENY","compareAtPrice":null,"inventoryManagement":"SHOPIFY","createdAt":"2022-03-06T22:09:20Z","updatedAt":"2023-10-27T16:56:00Z","taxable":true,"barcode":"","weight":112.0,"weightUnit":"GRAMS","inventoryQuantity":2,"requiresShipping":true,"availableForSale":true,"displayName":"4 Ounce Soy Candle - Test Variant 1","taxCode":"","grams":112.0,"image":null,"old_inventory_quantity":2,"product":{"product_id":"gid:\/\/shopify\/Product\/6796220989629"},"fulfillmentService":{"fulfillment_service":"manual"},"inventoryItem":{"inventory_item_id":"gid:\/\/shopify\/InventoryItem\/43653682495677"}}
{"__typename":"ProductVariantPricePair","price":{"amount":"19.0","currencyCode":"USD"},"compareAtPrice":null,"__parentId":"gid:\/\/shopify\/ProductVariant\/41561955827901"}\n"""


@pytest.fixture
def inventory_items_jsonl_content_example():
    return """{"__typename":"InventoryItem","id":"gid:\/\/shopify\/InventoryItem\/44871665713341","harmonizedSystemCode":null,"provinceCodeOfOrigin":null,"updatedAt":"2023-04-14T10:29:27Z","createdAt":"2023-04-14T10:29:27Z","sku":"","tracked":true,"requiresShipping":false,"duplicateSkuCount":0,"unitCost":{"cost":"60.0","currency_code":"USD"},"countryCodeOfOrigin":null}
{"__typename":"InventoryItem","id":"gid:\/\/shopify\/InventoryItem\/45419395743933","harmonizedSystemCode":"330510","provinceCodeOfOrigin":null,"updatedAt":"2023-12-11T10:37:41Z","createdAt":"2023-12-11T10:37:41Z","sku":"123","tracked":true,"requiresShipping":true,"duplicateSkuCount":0,"unitCost":{"cost":"29.0","currency_code":"USD"},"countryCodeOfOrigin":"UA"}\n"""


@pytest.fixture
def customer_address_jsonl_content_example():
    return """{"__typename":"Customer","id":"gid:\/\/shopify\/Customer\/123","defaultAddress":{"id":"gid:\/\/shopify\/MailingAddress\/123?model_name=CustomerAddress"},"addresses":[{"address1":"My Best Accent","address2":"","city":"Fair Lawn","country":"United States","countryCode":"US","company":"Test Company","firstName":"New Test","id":"gid:\/\/shopify\/MailingAddress\/123?model_name=CustomerAddress","lastName":"Customer","name":"New Test Customer","phone":"","province":"New Jersey","provinceCode":"NJ","zip":"07410"}],"updatedAt":"2023-04-24T13:53:48Z"}
{"__typename":"Customer","id":"gid:\/\/shopify\/Customer\/456","defaultAddress":{"id":"gid:\/\/shopify\/MailingAddress\/456?model_name=CustomerAddress"},"addresses":[{"address1":null,"address2":null,"city":null,"country":null,"countryCode":null,"company":null,"firstName":"MArcos","id":"gid:\/\/shopify\/MailingAddress\/456?model_name=CustomerAddress","lastName":"Millnitz","name":"MArcos Millnitz","phone":null,"province":null,"provinceCode":null,"zip":null}],"updatedAt":"2023-07-11T20:07:45Z"}\n"""


@pytest.fixture
def inventory_levels_jsonl_content_example():
    return """{"__typename":"Location","id":"gid:\/\/shopify\/Location\/63590301885"}
{"__typename":"InventoryLevel","id":"gid:\/\/shopify\/InventoryLevel\/97912455357?inventory_item_id=42185200631997","canDeactivate":false,"createdAt":"2021-06-23T01:09:47Z","deactivationAlert":"Can't unstock from this location because it has committed inventory.","updatedAt":"2023-04-13T12:00:55Z","item":{"inventory_history_url":"https:\/\/airbyte-integration-test.myshopify.com\/admin\/products\/inventory\/42185200631997\/inventory_history","inventory_item_id":"gid:\/\/shopify\/InventoryItem\/42185200631997","locations_count":{"count":1}},"quantities":[{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=available","name":"available","quantity":15,"updatedAt":"2023-04-13T12:00:55Z"},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=incoming","name":"incoming","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=committed","name":"committed","quantity":0,"updatedAt":"2022-03-17T10:05:08Z"},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=damaged","name":"damaged","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=on_hand","name":"on_hand","quantity":15,"updatedAt":"2023-04-13T12:00:52Z"},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=quality_control","name":"quality_control","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=reserved","name":"reserved","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185200631997\u0026name=safety_stock","name":"safety_stock","quantity":0,"updatedAt":null}],"__parentId":"gid:\/\/shopify\/Location\/63590301885"}
{"__typename":"InventoryLevel","id":"gid:\/\/shopify\/InventoryLevel\/97912455357?inventory_item_id=42185218719933","canDeactivate":false,"createdAt":"2021-06-23T01:10:48Z","deactivationAlert":"Can't unstock from this location because it has committed inventory.","updatedAt":"2023-04-13T12:09:45Z","item":{"inventory_history_url":"https:\/\/airbyte-integration-test.myshopify.com\/admin\/products\/inventory\/42185218719933\/inventory_history","inventory_item_id":"gid:\/\/shopify\/InventoryItem\/42185218719933","locations_count":{"count":1}},"quantities":[{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=available","name":"available","quantity":8,"updatedAt":"2023-04-13T12:09:45Z"},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=incoming","name":"incoming","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=committed","name":"committed","quantity":2,"updatedAt":"2023-04-13T12:09:45Z"},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=damaged","name":"damaged","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=on_hand","name":"on_hand","quantity":10,"updatedAt":"2023-04-13T12:09:45Z"},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=quality_control","name":"quality_control","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=reserved","name":"reserved","quantity":0,"updatedAt":null},{"id":"gid:\/\/shopify\/InventoryQuantity\/97912455357?inventory_item_id=42185218719933\u0026name=safety_stock","name":"safety_stock","quantity":0,"updatedAt":null}],"__parentId":"gid:\/\/shopify\/Location\/63590301885"}\n"""


@pytest.fixture
def discount_codes_jsonl_content_example():
    return """{"__typename":"DiscountCodeNode","id":"gid:\/\/shopify\/DiscountCodeNode\/945205379261","codeDiscount":{"__typename":"DiscountCodeFreeShipping","updatedAt":"2023-12-07T11:40:44Z","createdAt":"2021-07-08T12:40:37Z","discountType":"SHIPPING","startsAt":"2021-07-08T12:40:13Z","endsAt":"2024-01-02T07:59:59Z","status":"EXPIRED","title":"HZAVNV2487WC","usageLimit":null,"appliesOncePerCustomer":false,"asyncUsageCount":0,"codesCount":{"count":2},"totalSales":null,"summary":"Free shipping on all products • Minimum purchase of $1.00 • For all countries"}}
{"__typename":"DiscountRedeemCode","usageCount":0,"code":"HZAVNV2487WC","id":"gid:\/\/shopify\/DiscountRedeemCode\/11545139282109","createdBy":null,"__parentId":"gid:\/\/shopify\/DiscountCodeNode\/945205379261"}
{"__typename":"DiscountRedeemCode","usageCount":0,"code":"SUMMERSALE10OFF","id":"gid:\/\/shopify\/DiscountRedeemCode\/13175793582269","createdBy":null,"__parentId":"gid:\/\/shopify\/DiscountCodeNode\/945205379261"}\n"""


@pytest.fixture
def collections_jsonl_content_example():
    return """{"__typename":"Collection","id":"gid:\/\/shopify\/Collection\/270889287869","handle":"frontpage","title":"Home page","updatedAt":"2023-09-05T14:06:59Z","bodyHtml":"updated_mon_24.04.2023","sortOrder":"BEST_SELLING","templateSuffix":"","productsCount":{"products_count": 1}}
{"__typename":"CollectionPublication","publishedAt":"2021-06-23T01:00:25Z","__parentId":"gid:\/\/shopify\/Collection\/270889287869"}
{"__typename":"CollectionPublication","publishedAt":"2021-08-18T09:39:34Z","__parentId":"gid:\/\/shopify\/Collection\/270889287869"}
{"__typename":"CollectionPublication","publishedAt":"2023-04-20T11:12:24Z","__parentId":"gid:\/\/shopify\/Collection\/270889287869"}
{"__typename":"Collection","id":"gid:\/\/shopify\/Collection\/273278566589","handle":"test-collection","title":"Test Collection","updatedAt":"2023-09-05T14:12:04Z","bodyHtml":"updated_mon_24.04.2023","sortOrder":"BEST_SELLING","templateSuffix":"","productsCount":{"products_count": 26}}
{"__typename":"CollectionPublication","publishedAt":"2021-07-19T14:02:54Z","__parentId":"gid:\/\/shopify\/Collection\/273278566589"}
{"__typename":"CollectionPublication","publishedAt":"2021-08-18T09:39:34Z","__parentId":"gid:\/\/shopify\/Collection\/273278566589"}
{"__typename":"CollectionPublication","publishedAt":"2023-04-20T11:12:24Z","__parentId":"gid:\/\/shopify\/Collection\/273278566589"}\n"""


@pytest.fixture
def transactions_jsonl_content_example():
    return """{"__typename":"Order","id":"gid:\/\/shopify\/Order\/4554821468349","currency":"USD","transactions":[{"id":"gid:\/\/shopify\/OrderTransaction\/5721110872253","errorCode":null,"test":true,"kind":"SALE","amount":"57.23","createdAt":"2023-06-15T12:16:52Z","status":"SUCCESS","processedAt":"2023-06-15T12:16:52Z","gateway":"bogus","paymentId":"c25048437719229.1","accountNumber":"•••• •••• •••• 1","formattedGateway":"(For Testing) Bogus Gateway","manuallyCapturable":false,"receipt":"{}","parentTransaction":null,"authorization":"53433","totalUnsettledSet":{"presentmentMoney":{"amount":"0.0","currency":"USD"},"shopMoney":{"amount":"0.0","currency":"USD"}},"amountSet":{"shop_money":{"amount":"57.23","currency":"USD"}},"fees":[],"paymentDetails":{"avsResultCode":null,"cvvResultCode":null,"creditCardBin":"1","creditCardCompany":"Bogus","creditCardNumber":"•••• •••• •••• 1","creditCardName":"Bogus Gateway","creditCardWallet":null,"creditCardExpirationYear":2025,"creditCardExpirationMonth":2}},{"id":"gid:\/\/shopify\/OrderTransaction\/5721170968765","errorCode":null,"test":true,"kind":"REFUND","amount":"57.23","createdAt":"2022-06-15T13:25:42Z","status":"SUCCESS","processedAt":"2022-06-15T13:25:42Z","gateway":"bogus","paymentId":"c25048437719229.2","accountNumber":"•••• •••• •••• 1","formattedGateway":"(For Testing) Bogus Gateway","manuallyCapturable":false,"receipt":"{}","parentTransaction":{"parentId":"gid:\/\/shopify\/OrderTransaction\/5721110872253"},"authorization":null,"totalUnsettledSet":{"presentmentMoney":{"amount":"0.0","currency":"USD"},"shopMoney":{"amount":"0.0","currency":"USD"}},"amountSet":{"shop_money":{"amount":"57.23","currency":"USD"}},"fees":[],"paymentDetails":{"avsResultCode":null,"cvvResultCode":null,"creditCardBin":"1","creditCardCompany":"Bogus","creditCardNumber":"•••• •••• •••• 1","creditCardName":"Bogus Gateway","creditCardWallet":null,"creditCardExpirationYear":2025,"creditCardExpirationMonth":2}}]}\n"""


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
        "fulfill_at": "2023-04-24T18:00:00+00:00",
        "fulfill_by": None,
        "created_at": "2023-04-24T18:00:09+00:00",
        "updated_at": "2023-04-24T18:00:09+00:00",
        "request_status": "UNSUBMITTED",
        "status": "CLOSED",
        "channel_id": None,
        "assigned_location": {
            "address1": "Heroiv UPA 72",
            "address2": None,
            "city": "Lviv",
            "country_code": "UA",
            "name": "Heroiv UPA 72",
            "phone": "",
            "province": None,
            "zip": "30100",
            "location_id": 63590301885,
        },
        "destination": None,
        "delivery_method": {"id": 442031046845, "method_type": "SHIPPING", "min_delivery_date_time": None, "max_delivery_date_time": None},
        "international_duties": None,
        "fulfillment_holds": [],
        "supported_actions": [],
        "admin_graphql_api_id": "gid://shopify/FulfillmentOrder/2",
        "shop_id": None,
        "order_id": 1,
        "assigned_location_id": 63590301885,
        "line_items": [
            {
                "id": 3,
                "inventory_item_id": 43653688524989,
                "shop_id": None,
                "fulfillment_order_id": 2,
                "quantity": 1,
                "line_item_id": 12247585521853,
                "fulfillable_quantity": 0,
                "variant_id": 41561961824445,
            }
        ],
        "merchant_requests": [{"id": 333, "message": None, "kind": "FULFILLMENT_REQUEST", "request_options": {"notify_customer": True}}],
        "shop_url": "test_shop",
    }


@pytest.fixture
def order_risks_response_expected_result():
    return [
        {
            "updated_at": "2023-09-19T14:29:22+00:00",
            "id": 3945528492221,
            "order_id": 3945528492221,
            "admin_graphql_api_id": "gid://shopify/Order/3945528492221",
            "recommendation": "CANCEL",
            "assessments": [
                {
                    "risk_level": "NONE",
                    "facts": [
                        {"description": "Card Verification Value (CVV) isn't available", "sentiment": "NEUTRAL"},
                        {"description": "Billing address or credit card's address wasn't available", "sentiment": "NEUTRAL"},
                        {
                            "description": "Billing address ZIP or postal code isn't available to match with credit card's registered address",
                            "sentiment": "NEUTRAL",
                        },
                        {"description": "The payment method used isn't available", "sentiment": "NEUTRAL"},
                        {"description": "Location of IP address used to place the order isn't available", "sentiment": "NEUTRAL"},
                        {
                            "description": "Distance between shipping address and location of IP address isn't available",
                            "sentiment": "NEUTRAL",
                        },
                        {
                            "description": "The billing country or the country of the IP used to place the order isn't available",
                            "sentiment": "NEUTRAL",
                        },
                        {
                            "description": "Can't determine if a high risk internet connection was used because the IP address isn't available",
                            "sentiment": "NEUTRAL",
                        },
                        {"description": "There was 1 payment attempt", "sentiment": "POSITIVE"},
                    ],
                    "provider": None,
                },
                {
                    "risk_level": "HIGH",
                    "facts": [{"description": "This order came from an anonymous proxy", "sentiment": "NEGATIVE"}],
                    "provider": {
                        "features": [],
                        "description": None,
                        "handle": None,
                        "embedded": False,
                        "title": "Airbyte Test",
                        "published": False,
                        "developer_name": "app developer",
                        "developer_type": "MERCHANT",
                        "app_store_app_url": None,
                        "install_url": None,
                        "app_store_developer_url": None,
                        "is_post_purchase_app_in_use": False,
                        "previously_installed": False,
                        "pricing_details_summary": "Free",
                        "pricing_details": None,
                        "privacy_policy_url": None,
                        "public_category": "CUSTOM",
                        "uninstall_message": "You won't be able to view or access features for this app anymore. Discounts that use this app will also be deleted.",
                        "webhook_api_version": "2023-04",
                        "shopify_developed": False,
                        "provider_id": 5505221,
                        "failed_requirements": [],
                        "feedback": None,
                        "admin_graphql_api_id": "gid://shopify/App/5505221",
                    },
                },
            ],
            "shop_url": "test_shop",
        }
    ]


@pytest.fixture
def products_response_expected_result():
    return {
        "id": 123,
        "published_at": "2021-06-23T01:09:29+00:00",
        "created_at": "2021-06-23T01:09:29+00:00",
        "status": "ACTIVE",
        "vendor": "Blanda, O'Kon and Bartell",
        "updated_at": "2023-04-20T11:12:26+00:00",
        "body_html": "Gold and silver glitter iPhone 7 cases with geometric line patterns, stacked",
        "product_type": "Music",
        "tags": "developer-tools-generator",
        "handle": "gold-silver-iphone-7-case",
        "template_suffix": None,
        "title": "Gold Silver iPhone 7 Case",
        "description": "Gold and silver glitter iPhone 7 cases with geometric line patterns, stacked",
        "description_html": "Gold and silver glitter iPhone 7 cases with geometric line patterns, stacked",
        "is_gift_card": False,
        "legacy_resource_id": "123",
        "online_store_preview_url": "https://airbyte-integration-test.myshopify.com/products/gold-silver-iphone-7-case",
        "online_store_url": None,
        "total_inventory": 58,
        "tracks_inventory": True,
        "has_only_default_variant": False,
        "has_out_of_stock_variants": False,
        "requires_selling_plan": False,
        "price_range_v2": {
            "max_variant_price": {"amount": 99.0, "currency_code": "USD"},
            "min_variant_price": {"amount": 98.0, "currency_code": "USD"},
        },
        "featured_image": {
            "height": 3709,
            "id": "gid://shopify/ProductImage/29301295579325",
            "url": "https://cdn.shopify.com/s/files/1/0580/3317/6765/products/gold-silver-iphone-7-case.jpg?v=1624410569",
            "width": 5563,
            "alt_text": None,
        },
        "seo": {"description": None, "title": None},
        "featured_media": {
            "alt": "",
            "id": "gid://shopify/MediaImage/21562154123453",
            "status": "READY",
            "media_content_type": "IMAGE",
            "preview": {"status": "READY", "image": {"id": "gid://shopify/ImageSource/21570958426301", "alt_text": ""}},
            "media_errors": [],
            "media_warnings": [],
        },
        "feedback": None,
        "total_variants": 2,
        "media_count": 1,
        "options": [{"id": 8720175628477, "name": "Title", "values": ["Plastic", "indigo"], "position": 1, "product_id": 123}],
        "admin_graphql_api_id": "gid://shopify/Product/123",
        "images": [{"id": 111}],
        "variants": [{"id": 111}, {"id": 222}],
        "shop_url": "test_shop",
    }


@pytest.fixture
def product_images_response_expected_result():
    return [
        {
            "created_at": "2023-01-06T18:29:17+00:00",
            "updated_at": "2023-01-06T18:29:19+00:00",
            "id": 111,
            "height": 280,
            "alt": None,
            "src": "https://cdn.shopify.com/s/files/1/0580/3317/6765/products/white-t-shirt.jpg?v=1673029759",
            "width": 265,
            "admin_graphql_api_id": "gid://shopify/ProductImage/111",
            "product_id": 123,
            "shop_url": "test_shop",
        },
        {
            "created_at": "2021-06-23T01:09:47+00:00",
            "updated_at": "2023-04-24T17:27:15+00:00",
            "id": 222,
            "height": 1467,
            "alt": "updated_mon_24.04.2023",
            "src": "https://cdn.shopify.com/s/files/1/0580/3317/6765/products/4-ounce-soy-candle.jpg?v=1624410587",
            "width": 2200,
            "admin_graphql_api_id": "gid://shopify/ProductImage/222",
            "product_id": 456,
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def product_variants_response_expected_result():
    return [
        # sorted records in ASC, check the `updated_at` field
        {
            "id": 41561955827901,
            "title": "Test Variant 1",
            "price": 19.0,
            "sku": "",
            "position": 2,
            "inventory_policy": "DENY",
            "compare_at_price": None,
            "inventory_management": "SHOPIFY",
            "created_at": "2022-03-06T22:09:20+00:00",
            "updated_at": "2023-10-27T16:56:00+00:00",
            "taxable": True,
            "barcode": "",
            "weight": 112.0,
            "weight_unit": "GRAMS",
            "inventory_quantity": 2,
            "requires_shipping": True,
            "available_for_sale": True,
            "display_name": "4 Ounce Soy Candle - Test Variant 1",
            "tax_code": "",
            "grams": 112,
            "old_inventory_quantity": 2,
            "fulfillment_service": "manual",
            "admin_graphql_api_id": "gid://shopify/ProductVariant/41561955827901",
            "presentment_prices": [{"price": {"amount": 19.0, "currency_code": "USD"}, "compare_at_price": {"amount": None}}],
            "product_id": 6796220989629,
            "inventory_item_id": 43653682495677,
            "image_id": None,
            "shop_url": "test_shop",
        },
        {
            "id": 40091751448765,
            "title": "Metal",
            "price": 64.0,
            "sku": "",
            "position": 1,
            "inventory_policy": "DENY",
            "compare_at_price": None,
            "inventory_management": "SHOPIFY",
            "created_at": "2021-06-23T06:04:41+00:00",
            "updated_at": "2023-10-27T16:56:50+00:00",
            "taxable": True,
            "barcode": None,
            "weight": 0.0,
            "weight_unit": "GRAMS",
            "inventory_quantity": 6,
            "requires_shipping": False,
            "available_for_sale": True,
            "display_name": "Waterproof iPhone Speaker - Metal",
            "tax_code": "",
            "grams": 0,
            "old_inventory_quantity": 6,
            "fulfillment_service": "manual",
            "admin_graphql_api_id": "gid://shopify/ProductVariant/40091751448765",
            "presentment_prices": [{"price": {"amount": 64.0, "currency_code": "USD"}, "compare_at_price": {"amount": None}}],
            "product_id": 6796825198781,
            "inventory_item_id": 42186366255293,
            "image_id": None,
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def inventory_items_response_expected_result():
    return [
        {
            "id": 44871665713341,
            "harmonized_system_code": None,
            "province_code_of_origin": None,
            "updated_at": "2023-04-14T10:29:27+00:00",
            "created_at": "2023-04-14T10:29:27+00:00",
            "sku": "",
            "tracked": True,
            "requires_shipping": False,
            "duplicate_sku_count": 0,
            "country_code_of_origin": None,
            "admin_graphql_api_id": "gid://shopify/InventoryItem/44871665713341",
            "cost": 60.0,
            "currency_code": "USD",
            "country_harmonized_system_codes": [],
            "shop_url": "test_shop",
        },
        {
            "id": 45419395743933,
            "harmonized_system_code": "330510",
            "province_code_of_origin": None,
            "updated_at": "2023-12-11T10:37:41+00:00",
            "created_at": "2023-12-11T10:37:41+00:00",
            "sku": "123",
            "tracked": True,
            "requires_shipping": True,
            "duplicate_sku_count": 0,
            "country_code_of_origin": "UA",
            "admin_graphql_api_id": "gid://shopify/InventoryItem/45419395743933",
            "cost": 29.0,
            "currency_code": "USD",
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
            "shop_url": "test_shop",
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
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def inventory_levels_response_expected_result():
    return [
        {
            "id": "63590301885|42185200631997",
            "can_deactivate": False,
            "created_at": "2021-06-23T01:09:47Z",
            "deactivation_alert": "Can't unstock from this location because it has committed inventory.",
            "updated_at": "2023-04-13T12:00:55+00:00",
            "quantities": [
                {
                    "id": 97912455357,
                    "name": "available",
                    "quantity": 15,
                    "updatedAt": "2023-04-13T12:00:55+00:00",
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=available",
                },
                {
                    "id": 97912455357,
                    "name": "incoming",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=incoming",
                },
                {
                    "id": 97912455357,
                    "name": "committed",
                    "quantity": 0,
                    "updatedAt": "2022-03-17T10:05:08+00:00",
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=committed",
                },
                {
                    "id": 97912455357,
                    "name": "damaged",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=damaged",
                },
                {
                    "id": 97912455357,
                    "name": "on_hand",
                    "quantity": 15,
                    "updatedAt": "2023-04-13T12:00:52+00:00",
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=on_hand",
                },
                {
                    "id": 97912455357,
                    "name": "quality_control",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=quality_control",
                },
                {
                    "id": 97912455357,
                    "name": "reserved",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=reserved",
                },
                {
                    "id": 97912455357,
                    "name": "safety_stock",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185200631997&name=safety_stock",
                },
            ],
            "admin_graphql_api_id": "gid://shopify/InventoryLevel/97912455357?inventory_item_id=42185200631997",
            "inventory_item_id": 42185200631997,
            "inventory_history_url": "https://airbyte-integration-test.myshopify.com/admin/products/inventory/42185200631997/inventory_history",
            "locations_count": {"count": 1},
            "location_id": 63590301885,
            "shop_url": "test_shop",
        },
        {
            "id": "63590301885|42185218719933",
            "can_deactivate": False,
            "created_at": "2021-06-23T01:10:48Z",
            "deactivation_alert": "Can't unstock from this location because it has committed inventory.",
            "updated_at": "2023-04-13T12:09:45+00:00",
            "quantities": [
                {
                    "id": 97912455357,
                    "name": "available",
                    "quantity": 8,
                    "updatedAt": "2023-04-13T12:09:45+00:00",
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=available",
                },
                {
                    "id": 97912455357,
                    "name": "incoming",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=incoming",
                },
                {
                    "id": 97912455357,
                    "name": "committed",
                    "quantity": 2,
                    "updatedAt": "2023-04-13T12:09:45+00:00",
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=committed",
                },
                {
                    "id": 97912455357,
                    "name": "damaged",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=damaged",
                },
                {
                    "id": 97912455357,
                    "name": "on_hand",
                    "quantity": 10,
                    "updatedAt": "2023-04-13T12:09:45+00:00",
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=on_hand",
                },
                {
                    "id": 97912455357,
                    "name": "quality_control",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=quality_control",
                },
                {
                    "id": 97912455357,
                    "name": "reserved",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=reserved",
                },
                {
                    "id": 97912455357,
                    "name": "safety_stock",
                    "quantity": 0,
                    "updatedAt": None,
                    "admin_graphql_api_id": "gid://shopify/InventoryQuantity/97912455357?inventory_item_id=42185218719933&name=safety_stock",
                },
            ],
            "admin_graphql_api_id": "gid://shopify/InventoryLevel/97912455357?inventory_item_id=42185218719933",
            "inventory_item_id": 42185218719933,
            "inventory_history_url": "https://airbyte-integration-test.myshopify.com/admin/products/inventory/42185218719933/inventory_history",
            "locations_count": {"count": 1},
            "location_id": 63590301885,
            "shop_url": "test_shop",
        },
    ]


@pytest.fixture
def discount_codes_response_expected_result():
    return [
        {
            "usage_count": 0,
            "code": "HZAVNV2487WC",
            "id": 11545139282109,
            "created_by": None,
            "admin_graphql_api_id": "gid://shopify/DiscountRedeemCode/11545139282109",
            "price_rule_id": 945205379261,
            "typename": "DiscountCodeFreeShipping",
            "updated_at": "2023-12-07T11:40:44+00:00",
            "created_at": "2021-07-08T12:40:37+00:00",
            "discount_type": "SHIPPING",
            "starts_at": "2021-07-08T12:40:13Z",
            "ends_at": "2024-01-02T07:59:59Z",
            "status": "EXPIRED",
            "title": "HZAVNV2487WC",
            "usage_limit": None,
            "applies_once_per_customer": False,
            "async_usage_count": 0,
            "codes_count": {"count": 2},
            "total_sales": None,
            "summary": "Free shipping on all products \u2022 Minimum purchase of $1.00 \u2022 For all countries",
            "shop_url": "test_shop",
        },
        {
            "usage_count": 0,
            "code": "SUMMERSALE10OFF",
            "id": 13175793582269,
            "created_by": None,
            "admin_graphql_api_id": "gid://shopify/DiscountRedeemCode/13175793582269",
            "price_rule_id": 945205379261,
            "typename": "DiscountCodeFreeShipping",
            "updated_at": "2023-12-07T11:40:44+00:00",
            "created_at": "2021-07-08T12:40:37+00:00",
            "discount_type": "SHIPPING",
            "starts_at": "2021-07-08T12:40:13Z",
            "ends_at": "2024-01-02T07:59:59Z",
            "status": "EXPIRED",
            "title": "HZAVNV2487WC",
            "usage_limit": None,
            "applies_once_per_customer": False,
            "async_usage_count": 0,
            "codes_count": {"count": 2},
            "total_sales": None,
            "summary": "Free shipping on all products \u2022 Minimum purchase of $1.00 \u2022 For all countries",
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
        "id": 5721110872253,
        "error_code": None,
        "test": True,
        "kind": "SALE",
        "amount": 57.23,
        "created_at": "2023-06-15T12:16:52+00:00",
        "status": "SUCCESS",
        "processed_at": "2023-06-15T12:16:52+00:00",
        "gateway": "bogus",
        "payment_id": "c25048437719229.1",
        "account_number": "\u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 1",
        "formatted_gateway": "(For Testing) Bogus Gateway",
        "manually_capturable": False,
        "receipt": "{}",
        "authorization": "53433",
        "total_unsettled_set": {
            "presentment_money": {"amount": 0.0, "currency": "USD"},
            "shop_money": {"amount": 0.0, "currency": "USD"},
        },
        "amount_set": {"shop_money": {"amount": 57.23, "currency": "USD"}},
        "fees": [],
        "payment_details": {
            "avs_result_code": None,
            "cvv_result_code": None,
            "credit_card_bin": "1",
            "credit_card_company": "Bogus",
            "credit_card_number": "\u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 1",
            "credit_card_name": "Bogus Gateway",
            "credit_card_wallet": None,
            "credit_card_expiration_year": 2025,
            "credit_card_expiration_month": 2,
        },
        "order_id": 4554821468349,
        "currency": "USD",
        "admin_graphql_api_id": "gid://shopify/OrderTransaction/5721110872253",
        "parent_id": None,
        "shop_url": "test_shop",
    }
