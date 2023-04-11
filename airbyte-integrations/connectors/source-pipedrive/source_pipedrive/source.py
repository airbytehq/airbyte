#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from source_pipedrive.auth import QueryStringTokenAuthenticator
from source_pipedrive.streams import (
    Activities,
    ActivityFields,
    ActivityTypes,
    Currencies,
    DealFields,
    DealProducts,
    Deals,
    Files,
    Filters,
    LeadLabels,
    Leads,
    Notes,
    OrganizationFields,
    Organizations,
    PermissionSets,
    PersonFields,
    Persons,
    Pipelines,
    ProductFields,
    Products,
    Roles,
    Stages,
    Users,
)


class SourcePipedrive(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any]):
        config["replication_start_date"] = pendulum.parse(config["replication_start_date"])
        return config

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        config = self._validate_and_transform(config)
        try:
            stream = Deals(authenticator=self.get_authenticator(config), replication_start_date=config["replication_start_date"])
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records, None)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Pipedrive API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = self._validate_and_transform(config)
        stream_kwargs = {"authenticator": self.get_authenticator(config)}
        incremental_kwargs = {**stream_kwargs, "replication_start_date": config["replication_start_date"]}
        deals_stream = Deals(**incremental_kwargs)
        streams = [
            Activities(**incremental_kwargs),
            ActivityFields(**stream_kwargs),
            ActivityTypes(**incremental_kwargs),
            Currencies(**stream_kwargs),
            deals_stream,
            DealProducts(parent=deals_stream, **stream_kwargs),
            DealFields(**stream_kwargs),
            Files(**incremental_kwargs),
            Filters(**incremental_kwargs),
            LeadLabels(**stream_kwargs),
            Leads(**stream_kwargs),
            Notes(**incremental_kwargs),
            Organizations(**incremental_kwargs),
            OrganizationFields(**stream_kwargs),
            PermissionSets(**stream_kwargs),
            Persons(**incremental_kwargs),
            PersonFields(**stream_kwargs),
            Pipelines(**incremental_kwargs),
            ProductFields(**stream_kwargs),
            Products(**incremental_kwargs),
            Roles(**stream_kwargs),
            Stages(**incremental_kwargs),
            Users(**incremental_kwargs),
        ]
        return streams

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        authorization = config.get("authorization")
        if authorization:
            if authorization["auth_type"] == "Client":
                return Oauth2Authenticator(
                    token_refresh_endpoint="https://oauth.pipedrive.com/oauth/token",
                    client_id=authorization["client_id"],
                    client_secret=authorization["client_secret"],
                    refresh_token=authorization["refresh_token"],
                )
            elif authorization["auth_type"] == "Token":
                return QueryStringTokenAuthenticator(api_token=authorization["api_token"])
        # backward compatibility
        return QueryStringTokenAuthenticator(api_token=config["api_token"])
