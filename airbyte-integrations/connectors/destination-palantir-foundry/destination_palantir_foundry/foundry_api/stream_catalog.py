from typing import List, Optional

from foundry._core.auth_utils import Auth
from foundry.api_client import RequestInfo
from pydantic import BaseModel, RootModel

from destination_palantir_foundry.foundry_api.config import REQUEST_TIMEOUT, HEADERS
from destination_palantir_foundry.foundry_api.service import FoundryApiClient
from destination_palantir_foundry.foundry_api.service import FoundryService

STREAM_CATALOG = "stream-catalog"


class PartialStreamSettings(BaseModel):
    streamTypes: List[str]


class CreateStream2Request(BaseModel):
    parentRid: str
    name: str
    branch: str
    settings: PartialStreamSettings
    isRaw: bool
    markings: List[str]


class StreamView(BaseModel):
    viewRid: str
    datasetRid: str
    branch: str
    topicRid: str
    startTransactionRid: str
    isRaw: bool


class CreateStreamOrViewResponse(BaseModel):
    view: StreamView


class StreamSettings(BaseModel):
    partitions: int
    streamTypes: List[str]


class GetStreamResponse(BaseModel):
    view: StreamView
    streamSettings: StreamSettings


MaybeGetStreamResponse = RootModel[Optional[GetStreamResponse]]


class DeletedView(BaseModel):
    viewRid: str
    topicRid: str
    branch: str


class DeleteStreamResponse(BaseModel):
    deletedViews: List[DeletedView]


class StreamCatalog(FoundryService):
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryApiClient(
            foundry_host, api_auth, STREAM_CATALOG)

    def create_stream(self, parent_rid: str, name: str) -> CreateStreamOrViewResponse:
        request_body = CreateStream2Request(
            parentRid=parent_rid,
            name=name,
            branch="master",
            settings={"streamTypes": ["HIGH_THROUGHPUT"]},
            isRaw=True,
            markings=[],
            request_timeout=REQUEST_TIMEOUT,
        )

        create_stream_request = RequestInfo(
            method="POST",
            resource_path="/catalog/streams2",
            response_type=CreateStreamOrViewResponse,
            query_params={},
            path_params={},
            header_params=HEADERS,
            body_type=CreateStream2Request,
            body=request_body,
            request_timeout=REQUEST_TIMEOUT,
        )

        return self.api_client.call_api(create_stream_request)

    def get_stream(self, dataset_rid: str) -> MaybeGetStreamResponse:
        get_stream_request = RequestInfo(
            method="GET",
            resource_path="/catalog/streams/{dataset_rid}/branches/master/views/latest",
            response_type=MaybeGetStreamResponse,
            query_params={},
            path_params={
                "dataset_rid": dataset_rid
            },
            header_params=HEADERS,
            body_type=None,
            body=None,
            request_timeout=REQUEST_TIMEOUT,
        )

        return self.api_client.call_api(get_stream_request)

    def delete_stream(self, dataset_rid: str) -> DeleteStreamResponse:
        delete_stream_request = RequestInfo(
            method="DELETE",
            resource_path="/catalog/streams/{dataset_rid}",
            response_type=DeleteStreamResponse,
            query_params={},
            path_params={
                "dataset_rid": dataset_rid
            },
            header_params=HEADERS,
            body_type=None,
            body=None,
            request_timeout=REQUEST_TIMEOUT,
        )

        return self.api_client.call_api(delete_stream_request)
