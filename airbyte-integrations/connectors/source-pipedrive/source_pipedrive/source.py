#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from source_pipedrive.streams import (
    Activities,
    ActivityFields,
    DealFields,
    Deals,
    Leads,
    OrganizationFields,
    Organizations,
    PersonFields,
    Persons,
    Pipelines,
    Stages,
    Users,
)


class SourcePipedrive(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stream_kwargs = self.get_stream_kwargs(config)
            deals = Deals(**stream_kwargs)
            deals_gen = deals.read_records(sync_mode=SyncMode.full_refresh)
            next(deals_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Pipedrive API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        stream_kwargs = self.get_stream_kwargs(config)
        incremental_kwargs = {**stream_kwargs, "replication_start_date": pendulum.parse(config["replication_start_date"])}
        streams = [
            Activities(**incremental_kwargs),
            ActivityFields(**stream_kwargs),
            Deals(**incremental_kwargs),
            DealFields(**stream_kwargs),
            Leads(**stream_kwargs),
            Organizations(**incremental_kwargs),
            OrganizationFields(**stream_kwargs),
            Persons(**incremental_kwargs),
            PersonFields(**stream_kwargs),
            Pipelines(**incremental_kwargs),
            Stages(**incremental_kwargs),
            Users(**incremental_kwargs),
        ]
        return streams

    @staticmethod
    def get_stream_kwargs(config: Mapping[str, Any]) -> Mapping[str, Any]:
        authorization = config.get("authorization", {})
        stream_kwargs = dict()

        auth_type = authorization.get("auth_type")
        if auth_type == "Client":
            stream_kwargs["authenticator"] = Oauth2Authenticator(
                token_refresh_endpoint="https://oauth.pipedrive.com/oauth/token",
                client_secret=authorization.get("client_secret"),
                client_id=authorization.get("client_id"),
                refresh_token=authorization.get("refresh_token"),
            )
        elif auth_type == "Token":
            stream_kwargs["authenticator"] = {"api_token": authorization.get("api_token")}
        # backward compatibility
        else:
            if config.get("api_token"):
                stream_kwargs["authenticator"] = {"api_token": config.get("api_token")}
            else:
                raise Exception(f"Invalid auth type: {auth_type}")

        return stream_kwargs
