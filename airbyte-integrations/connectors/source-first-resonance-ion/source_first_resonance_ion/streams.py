from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, TypedDict

import requests
from airbyte_cdk.sources.streams.http import HttpStream

from source_first_resonance_ion.config import ENDPOINTS, Environment, Region

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


class FirstResonancePageInfo(TypedDict):
    hasNextPage: bool
    hasPreviousPage: bool
    startCursor: str
    endCursor: str
    count: int
    totalCount: int


class Edge(TypedDict):
    node: dict[str, Any]
    cursor: str


class Edges(TypedDict):
    edges: List[Edge]


from typing import Generic, TypeVar
from typing import Protocol, TypeVar

T = TypeVar("T", bound=str)


class QueryResult(TypedDict):
    pageInfo: FirstResonancePageInfo
    edges: List[Edge]


KeyType = TypeVar("KeyType", bound=str)


class FirstResonanceResponseData(Dict[KeyType, QueryResult]):
    pass


class FirstResonanceResponse(TypedDict):
    data: FirstResonanceResponseData[str]


# Basic full refresh stream
class FirstResonanceIonStream(HttpStream, ABC):
    class NextPageToken(TypedDict):
        endCursor: str

    class QueryVariables(TypedDict):
        first: int
        after: str

    class RequestJson(TypedDict):
        query: str
        variables: FirstResonanceIonStream.QueryVariables

    page_size: int = 100

    def __init__(self, region: Region, environment: Environment, **kwargs):
        super().__init__(**kwargs)
        self.region: Region = region
        self.environment: Environment = environment

    @property
    def url_base(self) -> str:
        return ENDPOINTS[self.region][self.environment]["api"]

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> str:
        return "graphql"

    def next_page_token(self, response: requests.Response) -> Optional[NextPageToken]:
        responseData: FirstResonanceResponse = response.json()
        pageInfo = responseData["data"][self.query_name]["pageInfo"]
        hasNextPage = pageInfo["hasNextPage"]

        if not hasNextPage:
            return None

        return {"endCursor": pageInfo["endCursor"]}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] | None,
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> RequestJson | None:
        after = ""
        if next_page_token and self.page_size:
            after = next_page_token["endCursor"]

        return {
            "query": self.query,
            "variables": {"first": self.page_size, "after": after},
        }

    @staticmethod
    def camel_to_lower_camel(s: str) -> str:
        if not s:
            return ""
        return s[0].lower() + s[1:]

    @property
    def query_name(self) -> str:
        """A method for subclasses to implement that gets the query and the and the operation name for the graphql query"""
        className = self.__class__.__name__
        lowerCamelCaseClassName = self.camel_to_lower_camel(className)
        return lowerCamelCaseClassName

    @property
    def query(self) -> str:
        gqlQueryFilePath = "./source_first_resonance_ion/graphql/generated/queries/{}.gql".format(self.query_name)
        with open(gqlQueryFilePath, "r") as query_file:
            query_string = query_file.read()
            return query_string

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        responseJson: FirstResonanceResponse = response.json()
        records = responseJson["data"][self.query_name]["edges"]
        for record in records:
            yield record["node"]

    @property
    def primary_key(self) -> str | List[str] | List[List[str]] | None:
        return "id"

    @property
    def http_method(self) -> str:
        return "POST"


class PurchaseOrders(FirstResonanceIonStream):
    """Purchase Orders Stream"""


class Suppliers(FirstResonanceIonStream):
    """Suppliers Stream"""
