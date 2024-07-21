from dataclasses import dataclass
from typing import Mapping, Any


@dataclass
class ClientCredentialsAuth:
    client_id: str
    client_secret: str


@dataclass
class MaterializationMode:
    instance: str


@dataclass
class DestinationConfig:
    project_rid: str
    materialization_mode: MaterializationMode


@dataclass
class FoundryConfig:
    host: str
    auth: ClientCredentialsAuth
    destination_config: DestinationConfig

    @classmethod
    def from_raw(cls, data: Mapping[str, Any]):
        materialization_mode = MaterializationMode(
            instance=data["destination_config"]["materialization_mode"]["instance"]
        )

        destination_config = DestinationConfig(
            project_rid=data["destination_config"]["project_rid"],
            materialization_mode=materialization_mode
        )

        auth = ClientCredentialsAuth(
            client_id=data["auth"]["client_id"],
            client_secret=data["auth"]["client_secret"]
        )

        return cls(
            host=data["host"],
            auth=auth,
            destination_config=destination_config
        )
