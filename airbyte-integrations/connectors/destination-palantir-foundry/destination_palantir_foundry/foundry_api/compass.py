from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.service import FoundryService
from foundry.api_client import RequestInfo
from foundry._core.auth_utils import Auth
from pydantic import BaseModel
from typing import List, Dict, Optional


COMPASS = "compass"


class DecoratedResource(BaseModel):
    rid: str
    name: str


class MaybeDecoratedResource(BaseModel):
    __root__: Optional[DecoratedResource]


class Rids(BaseModel):
    __root__: List[str]


class GetPathsResponse(BaseModel):
    __root__: Dict[str, str]


class Compass:
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryService(foundry_host, api_auth, COMPASS)

    def get_resource(self, rid: str) -> DecoratedResource:
        get_resource_request = RequestInfo(
            method="GET",
            resource_path="/resources/{rid}",
            response_type=DecoratedResource,
            query_params={},
            path_params={"rid": rid}
        )

        return self.api_client.call_api(get_resource_request)

    def get_paths(self, rids: List[str]) -> GetPathsResponse:
        get_paths_request = RequestInfo(
            method="POST",
            resource_path="/batch/paths",
            response_type=GetPathsResponse,
            query_params={},
            path_params={},
            body_type=Rids,
            body=rids
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
        )

        return self.api_client.api_client(get_resource_by_path_request)


class CompassFactory:
    def create(self, config: FoundryConfig, api_auth: Auth) -> Compass:
        return Compass(config.host, api_auth)
