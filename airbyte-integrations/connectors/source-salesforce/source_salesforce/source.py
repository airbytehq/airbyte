#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from requests import codes, exceptions  # type: ignore[import]

from .api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS, UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .streams import BulkIncrementalSalesforceStream, BulkSalesforceStream, Describe, IncrementalSalesforceStream, SalesforceStream


class AirbyteStopSync(AirbyteTracedException):
    pass


class SourceSalesforce(AbstractSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.catalog = None

    @staticmethod
    def _get_sf_object(config: Mapping[str, Any]) -> Salesforce:
        sf = Salesforce(**config)
        sf.login()
        return sf

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            salesforce = self._get_sf_object(config)
            salesforce.describe()
        except exceptions.HTTPError as error:
            error_msg = f"An error occurred: {error.response.text}"
            try:
                error_data = error.response.json()[0]
            except (KeyError, requests.exceptions.JSONDecodeError):
                pass
            else:
                error_code = error_data.get("errorCode")
                if error.response.status_code == codes.FORBIDDEN and error_code == "REQUEST_LIMIT_EXCEEDED":
                    logger.warn(f"API Call limit is exceeded. Error message: '{error_data.get('message')}'")
                    error_msg = "API Call limit is exceeded"
            return False, error_msg
        return True, None

    @classmethod
    def _get_api_type(cls, stream_name, properties):
        # Salesforce BULK API currently does not support loading fields with data type base64 and compound data
        properties_not_supported_by_bulk = {
            key: value for key, value in properties.items() if value.get("format") == "base64" or "object" in value["type"]
        }
        properties_length = len(",".join(p for p in properties))

        rest_required = stream_name in UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS or properties_not_supported_by_bulk
        # If we have a lot of properties we can overcome REST API URL length and get an error: "reason: URI Too Long".
        # For such cases connector tries to use BULK API because it uses POST request and passes properties in the request body.
        bulk_required = properties_length + 2000 > Salesforce.REQUEST_SIZE_LIMITS

        if rest_required and not bulk_required:
            return "rest"
        if not rest_required:
            return "bulk"

    @classmethod
    def generate_streams(
        cls,
        config: Mapping[str, Any],
        stream_objects: Mapping[str, Any],
        sf_object: Salesforce,
    ) -> List[Stream]:
        """ "Generates a list of stream by their names. It can be used for different tests too"""
        authenticator = TokenAuthenticator(sf_object.access_token)
        stream_properties = sf_object.generate_schemas(stream_objects)
        streams = []
        for stream_name, sobject_options in stream_objects.items():
            streams_kwargs = {"sobject_options": sobject_options}
            selected_properties = stream_properties.get(stream_name, {}).get("properties", {})

            api_type = cls._get_api_type(stream_name, selected_properties)
            if api_type == "rest":
                full_refresh, incremental = SalesforceStream, IncrementalSalesforceStream
            elif api_type == "bulk":
                full_refresh, incremental = BulkSalesforceStream, BulkIncrementalSalesforceStream
            else:
                raise Exception(f"Stream {stream_name} cannot be processed by REST or BULK API.")

            json_schema = stream_properties.get(stream_name, {})
            pk, replication_key = sf_object.get_pk_and_replication_key(json_schema)
            streams_kwargs.update(dict(sf_api=sf_object, pk=pk, stream_name=stream_name, schema=json_schema, authenticator=authenticator))
            if replication_key and stream_name not in UNSUPPORTED_FILTERING_STREAMS:
                streams.append(incremental(**streams_kwargs, replication_key=replication_key, start_date=config.get("start_date")))
            else:
                streams.append(full_refresh(**streams_kwargs))

        return streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        sf = self._get_sf_object(config)
        stream_objects = sf.get_validated_streams(config=config, catalog=self.catalog)
        streams = self.generate_streams(config, stream_objects, sf)
        streams.append(Describe(sf_api=sf, catalog=self.catalog))
        return streams

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        # save for use inside streams method
        self.catalog = catalog
        try:
            yield from super().read(logger, config, catalog, state)
        except AirbyteStopSync:
            logger.info(f"Finished syncing {self.name}")

    def _read_stream(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        try:
            yield from super()._read_stream(logger, stream_instance, configured_stream, state_manager, internal_config)
        except exceptions.HTTPError as error:
            error_data = error.response.json()[0]
            error_code = error_data.get("errorCode")
            if error.response.status_code == codes.FORBIDDEN and error_code == "REQUEST_LIMIT_EXCEEDED":
                logger.warn(f"API Call limit is exceeded. Error message: '{error_data.get('message')}'")
                raise AirbyteStopSync()  # if got 403 rate limit response, finish the sync with success.
            raise error
