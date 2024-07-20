from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.service import FoundryService
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema
from foundry.api_client import RequestInfo
from foundry._core.auth_utils import Auth
from pydantic import BaseModel


FOUNDRY_METADATA = "foundry-metadata"


class FoundrySchemaVersionIdResponse(BaseModel):
    transactionRid: str
    versionId: str


class FoundryMetadata:
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryService(
            foundry_host, api_auth, FOUNDRY_METADATA)

    def put_schema(self, dataset_rid: str, foundry_schema: FoundrySchema) -> FoundrySchemaVersionIdResponse:
        get_resource_request = RequestInfo(
            method="GET",
            resource_path="/schemas/datasets/{dataset_rid}/branches/master",
            response_type=FoundrySchemaVersionIdResponse,
            query_params={},
            path_params={
                "dataset_rid": dataset_rid
            },
            body_type=FoundrySchema,
            body=foundry_schema
        )

        return self.api_client.call_api(get_resource_request)


class FoundryMetadataFactory:
    def create(self, config: FoundryConfig, api_auth: Auth) -> FoundryMetadata:
        return FoundryMetadata(config.host, api_auth)
