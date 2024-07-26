from foundry._core.auth_utils import Auth

from destination_palantir_foundry.foundry_api.compass import Compass
from destination_palantir_foundry.foundry_api.foundry_metadata import FoundryMetadata
from destination_palantir_foundry.foundry_api.service import FoundryService
from destination_palantir_foundry.foundry_api.stream_catalog import StreamCatalog
from destination_palantir_foundry.foundry_api.stream_proxy import StreamProxy


class FoundryServiceFactory:
    def __init__(self, host: str, api_auth: Auth) -> None:
        self.host = host
        self.auth = api_auth

    def compass(self) -> Compass:
        return self._instantiate_service(Compass)

    def stream_catalog(self):
        return self._instantiate_service(StreamCatalog)

    def stream_proxy(self):
        return self._instantiate_service(StreamProxy)

    def foundry_metadata(self):
        return self._instantiate_service(FoundryMetadata)

    def _instantiate_service(self, service: FoundryService):
        return service(self.host, self.auth)
