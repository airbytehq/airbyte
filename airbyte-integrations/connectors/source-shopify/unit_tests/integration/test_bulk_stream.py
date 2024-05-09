import pytest
import requests

from source_shopify import SourceShopify
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http import HttpResponse
from freezegun import freeze_time
from airbyte_protocol.models import SyncMode
from typing import Any, Dict
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest
from test_data import get_shop_response, get_scopes_response, get_status_graphql_response, get_data_graphql_response, \
    get_records_file_response
import pendulum as pdm


_JOB_START_DATE = pdm.parse("2024-05-05T00:00:00+00:00")
_JOB_END_DATE = _JOB_START_DATE.add(hours=2, minutes=24)

_URL_ACCESS_SCOPES = "https://airbyte-integration-test.myshopify.com/admin/oauth/access_scopes.json"
_URL_SHOP = "https://airbyte-integration-test.myshopify.com/admin/api/2023-07/shop.json"
_URL_GRAPHQL = "https://airbyte-integration-test.myshopify.com/admin/api/2023-07/graphql.json"
_URL_RECORDS_FILE = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/l6lersgk4i81iqc3n6iisywwtipb-final"

_BULK_STREAM = "metafield_orders"


def _get_config(start_date: str, bulk_window: int = 1) -> Dict[str, Any]:
    return {
        "start_date": start_date,
        "shop": "airbyte-integration-test",
        "credentials": {
            "auth_method": "api_password",
            "api_password": "api_password",
        },
        "bulk_window_in_days": bulk_window
    }


def _get_scopes_request() -> HttpRequest:
    return HttpRequest(
        url=_URL_ACCESS_SCOPES,
        query_params=ANY_QUERY_PARAMS,
    )


def _get_shop_request() -> HttpRequest:
    return HttpRequest(
        url=_URL_SHOP,
        query_params=ANY_QUERY_PARAMS,
    )


def _get_data_graphql_request() -> HttpRequest:
    return HttpRequest(
        url=_URL_GRAPHQL,
        body='{"query": "mutation {\\n                bulkOperationRunQuery(\\n                    query: \\"\\"\\"\\n                     {\\n  orders(\\n    query: \\"updated_at:>=\'2024-05-05T00:00:00+00:00\' AND updated_at:<=\'2024-05-05T02:24:00+00:00\'\\"\\n    sortKey: UPDATED_AT\\n  ) {\\n    edges {\\n      node {\\n        __typename\\n        id\\n        metafields {\\n          edges {\\n            node {\\n              __typename\\n              id\\n              namespace\\n              value\\n              key\\n              description\\n              createdAt\\n              updatedAt\\n              type\\n            }\\n          }\\n        }\\n      }\\n    }\\n  }\\n}\\n                    \\"\\"\\"\\n                ) {\\n                    bulkOperation {\\n                        id\\n                        status\\n                        createdAt\\n                    }\\n                    userErrors {\\n                        field\\n                        message\\n                    }\\n                }\\n            }"}'
    )


def _get_status_graphql_request() -> HttpRequest:
    return HttpRequest(
        url=_URL_GRAPHQL,
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


def _get_records_file_request() -> HttpRequest:
    return HttpRequest(
        url=_URL_RECORDS_FILE,
        query_params=ANY_QUERY_PARAMS,
    )


def _mock_successful_read_requests(http_mocker: HttpMocker):
    """Mock the multiple requests needed for a bulk GraphQL read.
    """
    http_mocker.get(
        _get_shop_request(),
        HttpResponse(get_shop_response())
    )
    http_mocker.get(
        _get_scopes_request(),
        HttpResponse(get_scopes_response())
    )
    http_mocker.post(
        _get_data_graphql_request(),
        HttpResponse(get_data_graphql_response())
    )
    http_mocker.post(
        _get_status_graphql_request(),
        HttpResponse(get_status_graphql_response())
    )
    http_mocker.get(
        _get_records_file_request(),
        HttpResponse(get_records_file_response())
    )


@freeze_time(_JOB_END_DATE)
def test_read_graphql_records_successfully():
    with HttpMocker() as http_mocker:
        _mock_successful_read_requests(http_mocker)

        catalog = CatalogBuilder().with_stream(_BULK_STREAM, SyncMode.full_refresh).build()
        output = read(SourceShopify(), _get_config(_JOB_START_DATE.to_date_string()), catalog)

        assert output.errors == []
        assert len(output.records) == 2


def _mock_failing_read_requests(http_mocker: HttpMocker):
    """Mock the multiple requests needed for a bulk GraphQL read with a failure and then a successful response.
    """
    http_mocker.get(
        _get_shop_request(),
        HttpResponse(get_shop_response())
    )
    http_mocker.get(
        _get_scopes_request(),
        HttpResponse(get_scopes_response())
    )
    inner_mocker = http_mocker.__getattribute__("_mocker")

    def raise_connectio_error(request, context):
        raise ConnectionError("ConnectionError")

    # Mock the first GraphQL request to fail with a ConnectionError, and then succeed in the next call.
    inner_mocker.register_uri(
        "POST",
        _URL_GRAPHQL,
        [{"text": raise_connectio_error}, {"text": get_data_graphql_response(), "status_code": 200}],
    )

    http_mocker.post(
        _get_status_graphql_request(),
        HttpResponse(get_status_graphql_response())
    )
    http_mocker.get(
        _get_records_file_request(),
        HttpResponse(get_records_file_response())
    )


@freeze_time(_JOB_END_DATE)
def test_check_for_errors_with_connection_error() -> None:
    with HttpMocker() as http_mocker:
        _mock_failing_read_requests(http_mocker)

        catalog = CatalogBuilder().with_stream(_BULK_STREAM, SyncMode.full_refresh).build()
        output = read(SourceShopify(), _get_config(_JOB_START_DATE.to_date_string()), catalog)

        assert "ConnectionError" in output.errors.__str__()

        # TODO: We should be able to read records once the retry logic is implemented in HTTPClient.
        # assert output.records == 2
