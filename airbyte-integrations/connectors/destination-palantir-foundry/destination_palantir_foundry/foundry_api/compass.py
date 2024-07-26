from json import JSONDecodeError
from typing import List, Dict, Optional

from foundry._core.auth_utils import Auth
from foundry.api_client import RequestInfo
from pydantic import BaseModel, RootModel

from destination_palantir_foundry.foundry_api.config import REQUEST_TIMEOUT, HEADERS
from destination_palantir_foundry.foundry_api.service import FoundryApiClient
from destination_palantir_foundry.foundry_api.service import FoundryService

COMPASS = "compass"


class DecoratedResource(BaseModel):
    rid: str
    name: str


MaybeDecoratedResource = RootModel[Optional[DecoratedResource]]

Rids = RootModel[List[str]]

GetPathsResponse = RootModel[Dict[str, str]]


class DeleteResult(BaseModel):
    rid: str
    type: str


DeleteResults = RootModel[List[DeleteResult]]


class Compass(FoundryService):
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryApiClient(foundry_host, api_auth, COMPASS)

    def get_resource(self, rid: str) -> DecoratedResource:
        get_resource_request = RequestInfo(
            method="GET",
            resource_path="/resources/{rid}",
            response_type=DecoratedResource,
            query_params={},
            path_params={"rid": rid},
            header_params=HEADERS,
            body=None,
            body_type=None,
            request_timeout=REQUEST_TIMEOUT,
        )

        return self.api_client.call_api(get_resource_request)

    def get_paths(self, rids: List[str]) -> GetPathsResponse:
        get_paths_request = RequestInfo(
            method="POST",
            resource_path="/batch/paths",
            response_type=GetPathsResponse,
            query_params={},
            path_params={},
            header_params=HEADERS,
            body_type=Rids,
            body=Rids(rids),
            request_timeout=REQUEST_TIMEOUT,
        )

        return self.api_client.call_api(get_paths_request)

    def get_resource_by_path(self, path: str) -> MaybeDecoratedResource:
        get_resource_by_path_request = RequestInfo(
            method="GET",
            resource_path="/resources",
            response_type=MaybeDecoratedResource,
            query_params={
                "path": path,
                "additionalOperations": []
            },
            path_params={},
            header_params=HEADERS,
            body_type=None,
            body=None,
            request_timeout=REQUEST_TIMEOUT,
        )

        try:
            return self.api_client.call_api(get_resource_by_path_request)
        except JSONDecodeError:
            return MaybeDecoratedResource(None)

    def delete_permanently(self, rids: List[str]) -> DeleteResults:
        delete_permanently_request = RequestInfo(
            method="POST",
            resource_path="/trash/delete",
            response_type=DeleteResults,
            query_params={
                "deleteOptions": ["DO_NOT_REQUIRE_TRASHED"]
            },
            path_params={},
            header_params=HEADERS,
            body=Rids(rids),
            body_type=Rids,
            request_timeout=REQUEST_TIMEOUT,
        )

        return self.api_client.call_api(delete_permanently_request)
