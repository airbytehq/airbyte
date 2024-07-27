from foundry._core.auth_utils import Auth
from foundry.api_client import RequestInfo
from pydantic import BaseModel

from destination_palantir_foundry.foundry_api.config import REQUEST_TIMEOUT, HEADERS
from destination_palantir_foundry.foundry_api.service import FoundryApiClient
from destination_palantir_foundry.foundry_api.service import FoundryService
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema

FOUNDRY_METADATA = "foundry-metadata"


class FoundrySchemaVersionIdResponse(BaseModel):
    transactionRid: str
    versionId: str


class FoundryMetadata(FoundryService):
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryApiClient(
            foundry_host, api_auth, FOUNDRY_METADATA)

    def put_schema(self, dataset_rid: str, foundry_schema: FoundrySchema) -> FoundrySchemaVersionIdResponse:
        get_resource_request = RequestInfo(
            method="POST",
            resource_path="/schemas/datasets/{dataset_rid}/branches/master",
            response_type=FoundrySchemaVersionIdResponse,
            query_params={},
            path_params={
                "dataset_rid": dataset_rid
            },
            header_params=HEADERS,
            body_type=FoundrySchema,
            body=foundry_schema,
            request_timeout=REQUEST_TIMEOUT,
        )

        s = foundry_schema
        a = foundry_schema.model_dump(exclude_unset=True, by_alias=True)
        
        print(s, a)

        return self.api_client.call_api(get_resource_request)
