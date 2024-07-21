from typing import Mapping, Any, Union, Literal

from pydantic import BaseModel, Field


class ClientCredentialsAuth(BaseModel):
    client_id: str
    client_secret: str


class FoundryStreamsMaterializationMode(BaseModel):
    instance: Literal["foundry_streams"]


class DestinationConfig(BaseModel):
    project_rid: str
    materialization_mode: Union[FoundryStreamsMaterializationMode] = Field(..., discriminator="instance")


class FoundryConfig(BaseModel):
    host: str
    auth: ClientCredentialsAuth
    destination_config: DestinationConfig

    @classmethod
    def from_raw(cls, data: Mapping[str, Any]):
        return FoundryConfig.model_validate(obj=data)
