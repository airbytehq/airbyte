#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Tuple, Union, MutableMapping, Iterator

import requests
from airbyte_cdk.models import AirbyteCatalog, AirbyteStream, ConfiguredAirbyteCatalog, AirbyteStateMessage, \
    AirbyteMessage
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import IncrementalMicrosoftDataverseStream

from .authenticator import Crm365Oauth2Authenticator


class SourceMicrosoftDataverse(AbstractSource):

    def __init__(self):
        self.catalogs = None

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        auth = Crm365Oauth2Authenticator(
            token_refresh_endpoint=f'https://login.microsoftonline.com/{config["tenant_id"]}/oauth2/v2.0/token',
            client_id=config["client_id"],
            client_secret=config["client_secret_value"],
            scopes=[f'{config["url"]}/.default'],
            refresh_token=None
        )
        headers = auth.get_auth_header()
        # Call a protected API with the access token.
        response = requests.get(
            config["url"] + "/api/data/v9.2/EntityDefinitions?$expand=Attributes",
            headers=headers,
        )
        response_json = response.json()
        streams = []
        for entity in response_json["value"]:
            schema = {
                "properties": {
                    "_ab_cdc_updated_at": {
                        "type": "string"
                    },
                    "_ab_cdc_deleted_at": {
                        "type": ["null", "string"]
                    }
                }
            }
            for attribute in entity["Attributes"]:
                if attribute["AttributeType"] == "String":
                    attribute_type = {"type": ["null", "string"]}
                elif attribute["AttributeType"] == "DateTime":
                    attribute_type = {"type": ["null", "string"], "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
                elif attribute["AttributeType"] == "Integer":
                    attribute_type = {"type": ["null", "integer"]}
                elif attribute["AttributeType"] == "Money":
                    attribute_type = {"type": ["null", "number"]}
                elif attribute["AttributeType"] == "Boolean":
                    attribute_type = {"type": ["null", "boolean"]}
                elif attribute["AttributeType"] == "Double":
                    attribute_type = {"type": ["null", "number"]}
                elif attribute["AttributeType"] == "Decimal":
                    attribute_type = {"type": ["null", "number"]}
                elif attribute["AttributeType"] == "Virtual":
                    continue
                else:
                    attribute_type = {"type": ["null", "string"]}

                schema["properties"][attribute["LogicalName"]] = attribute_type

            stream = AirbyteStream(name=entity["LogicalName"], json_schema=schema)
            stream.supported_sync_modes = ["full_refresh", "incremental"]
            stream.source_defined_cursor = True
            stream.default_cursor_field = ["_ab_cdc_updated_at"]
            stream.source_defined_primary_key = [[entity["PrimaryIdAttribute"]]]
            streams.append(stream)
        return AirbyteCatalog(streams=streams)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = Crm365Oauth2Authenticator(
                    token_refresh_endpoint=f'https://login.microsoftonline.com/{config["tenant_id"]}/oauth2/v2.0/token',
                    client_id=config["client_id"],
                    client_secret=config["client_secret_value"],
                    scopes=[f'{config["url"]}/.default'],
                    refresh_token=None
                    )
            headers = auth.get_auth_header()
            # Call a protected API with the access token.
            response = requests.get(
                config["url"] + "/api/data/v9.2/",
                headers=headers,
            )
            # Raises an exception for error codes (4xx or 5xx)
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        self.catalogs = catalog
        return super().read(logger, config, catalog, state)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = Crm365Oauth2Authenticator(
                token_refresh_endpoint=f'https://login.microsoftonline.com/{config["tenant_id"]}/oauth2/v2.0/token',
                client_id=config["client_id"],
                client_secret=config["client_secret_value"],
                scopes=[f'{config["url"]}/.default'],
                refresh_token=None
                )

        streams = []
        for catalog in self.catalogs.streams:
            streams.append(IncrementalMicrosoftDataverseStream(
                url=config["url"],
                stream_name=catalog.stream.name,
                primary_key=catalog.primary_key,
                schema=catalog.stream.json_schema,
                max_num_pages=config["max_num_pages"],
                odata_maxpagesize=config["odata_maxpagesize"],
                authenticator=auth)
            )
        return streams
