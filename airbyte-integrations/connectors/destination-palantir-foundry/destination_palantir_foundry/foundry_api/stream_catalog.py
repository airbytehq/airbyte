from destination_palantir_foundry.foundry_api.service import FoundryService
from pydantic import BaseModel
from foundry._core.auth_utils import Auth
from typing import List
from foundry.api_client import RequestInfo
from destination_palantir_foundry.config.foundry_config import FoundryConfig


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


class StreamCatalog:
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryService(
            foundry_host, api_auth, STREAM_CATALOG)

    def create_stream(self, parent_rid: str, name: str) -> CreateStreamOrViewResponse:
        request_body: CreateStream2Request = {
            "parentRid": parent_rid,
            "name": name,
            "branch": "master",
            "settings": {"streamTypes": ["HIGH_THROUGHPUT"]},
            "isRaw": True,
            "markings": []
        }

        create_stream_request = RequestInfo(
            method="GET",
            resource_path="/catalog/streams/{parent_rid}/branches/master/views/latest",
            response_type=CreateStreamOrViewResponse,
            query_params={},
            path_params={
                "parent_rid": parent_rid
            },
            body_type=CreateStream2Request,
            body=request_body
        )

        return self.api_client.call_api(create_stream_request)


class StreamCatalogFactory:
    def create(self, config: FoundryConfig, api_auth: Auth) -> StreamCatalog:
        return StreamCatalog(config.host, api_auth)
