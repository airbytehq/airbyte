import json
from datetime import datetime
from random import randint

from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


def _create_job_url(shop_name: str) -> str:
    return f"https://{shop_name}.myshopify.com/admin/api/2023-07/graphql.json"


def create_job_creation_request(shop_name: str, lower_boundary: datetime, upper_boundary: datetime) -> HttpRequest:
    outer_query = """mutation {
                bulkOperationRunQuery(
                    query: \"\"\"
                     %INNER_QUERY_TOKEN%
                    \"\"\"
                ) {
                    bulkOperation {
                        id
                        status
                        createdAt
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }"""
    inner_query = """{
  orders(
    query: \"updated_at:>='%LOWER_BOUNDARY_TOKEN%' AND updated_at:<='%UPPER_BOUNDARY_TOKEN%'\"
    sortKey: UPDATED_AT
  ) {
    edges {
      node {
        __typename
        id
        metafields {
          edges {
            node {
              __typename
              id
              namespace
              value
              key
              description
              createdAt
              updatedAt
              type
            }
          }
        }
      }
    }
  }
}"""
    inner_query = inner_query.replace("%LOWER_BOUNDARY_TOKEN%", lower_boundary.isoformat())
    inner_query = inner_query.replace("%UPPER_BOUNDARY_TOKEN%", upper_boundary.isoformat())
    outer_query = outer_query.replace("%INNER_QUERY_TOKEN%", inner_query)

    return HttpRequest(
        url=_create_job_url(shop_name),
        body=json.dumps({"query": outer_query})
    )


def create_job_status_request(shop_name: str, job_id: str) -> HttpRequest:
    return HttpRequest(
        url=_create_job_url(shop_name),
        body=f"""query {{
                    node(id: "{job_id}") {{
                        ... on BulkOperation {{
                            id
                            status
                            errorCode
                            createdAt
                            objectCount
                            fileSize
                            url
                            partialDataUrl
                        }}
                    }}
                }}"""
    )


class JobCreationResponseBuilder:
    def __init__(self) -> None:
        self._template = {
            "data": {
                "bulkOperationRunQuery": {
                    "bulkOperation": {
                        "id": "gid://shopify/BulkOperation/0",
                        "status": "CREATED",
                        "createdAt": "2024-05-05T02:00:00Z"
                    },
                    "userErrors": []
                }
            },
            "extensions": {
                "cost": {
                    "requestedQueryCost": 10,
                    "actualQueryCost": 10,
                    "throttleStatus": {
                        "maximumAvailable": 2000.0,
                        "currentlyAvailable": 1990,
                        "restoreRate": 100.0
                    }
                }
            }
        }

    def with_bulk_operation_id(self, bulk_operation_id: str) -> "JobCreationResponseBuilder":
        self._template["data"]["bulkOperationRunQuery"]["bulkOperation"]["id"] = bulk_operation_id
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(self._template), status_code=200)


class JobStatusResponseBuilder:
    def __init__(self) -> None:
        self._template = {
            "data": {
                "node": {},
                "extensions": {
                    "cost": {
                        "requestedQueryCost": 1,
                        "actualQueryCost": 1,
                        "throttleStatus": {
                            "maximumAvailable": 2000.0,
                            "currentlyAvailable": 1999,
                            "restoreRate": 100.0
                        }
                    }
                }
            }
        }

    def with_completed_status(self, bulk_operation_id: str, job_result_url: str) -> "JobStatusResponseBuilder":
        self._template["data"]["node"] = {
            "id": bulk_operation_id,
            "status": "COMPLETED",
            "errorCode": None,
            "createdAt": "2024-05-05T00:45:48Z",
            "objectCount": "4",
            "fileSize": "774",
            "url": job_result_url,
            "partialDataUrl": None
        }
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(self._template), status_code=200)


class MetafieldOrdersJobResponseBuilder:
    def __init__(self) -> None:
        self._records = []

    def _any_record(self) -> str:
        an_id = str(randint(1000000000000, 9999999999999))
        a_parent_id = str(randint(1000000000000, 9999999999999))
        return f"""{{"__typename":"Order","id":"gid:\/\/shopify\/Order\/{a_parent_id}"}}
{{"__typename":"Metafield","id":"gid:\/\/shopify\/Metafield\/{an_id}","namespace":"my_fields","value":"asdfasdf","key":"purchase_order","description":null,"createdAt":"2023-04-13T12:09:50Z","updatedAt":"2024-05-05T01:09:50Z","type":"single_line_text_field","__parentId":"gid:\/\/shopify\/Order\/{a_parent_id}"}}
"""


    def with_record(self) -> "MetafieldOrdersJobResponseBuilder":
        self._records.append(self._any_record())
        return self

    def build(self) -> HttpResponse:
        return HttpResponse("".join(self._records), status_code=200)
