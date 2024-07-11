from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.service import FoundryService
from destination_palantir_foundry.foundry_api.http import build_path
from foundry.api_client import RequestInfo
from foundry._core.auth_utils import Auth
from pydantic import BaseModel


COMPASS = "compass"


class DecoratedResource(BaseModel): # partial: https://spellbook.palantir.build/repo/Compass/api/version/3.1227.0?typeId=com.palantir.compass.api.DecoratedResource
    name: str


class Compass:
    def __init__(self, config: FoundryConfig, api_auth: Auth) -> None:
        self.api_client = FoundryService(config, api_auth, COMPASS)

    def get_resource(self, rid: str) -> DecoratedResource:
        get_resource_request = RequestInfo(
            method="GET",
            resource_path="/resources/{rid}",
            response_type=DecoratedResource,
            query_params={},
            path_params={"rid": rid}
        )
        
        return self.api_client.call_api(get_resource_request)
