#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import split_config
from requests import codes, exceptions  # type: ignore[import]

from .api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS, UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .streams import BulkIncrementalSalesforceStream, BulkSalesforceStream, Describe, IncrementalSalesforceStream, SalesforceStream


class SourceSalesforce(AbstractSource):
    @staticmethod
    def _get_sf_object(config: Mapping[str, Any]) -> Salesforce:
        sf = Salesforce(**config)
        sf.login()
        return sf

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            _ = self._get_sf_object(config)
        except exceptions.HTTPError as error:
            error_data = error.response.json()[0]
            error_code = error_data.get("errorCode")
            if error.response.status_code == codes.FORBIDDEN and error_code == "REQUEST_LIMIT_EXCEEDED":
                logger.warn(f"API Call limit is exceeded. Error message: '{error_data.get('message')}'")
                return False, "API Call limit is exceeded"

        return True, None

    @classmethod
    def _get_api_type(cls, stream_name, properties, stream_state):
        # Salesforce BULK API currently does not support loading fields with data type base64 and compound data
        properties_not_supported_by_bulk = {
            key: value for key, value in properties.items() if value.get("format") == "base64" or "object" in value["type"]
        }
        properties_length = len(",".join(p for p in properties))

        rest_required = stream_name in UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS or properties_not_supported_by_bulk
        # If we have a lot of properties we can overcome REST API URL length and get an error: "reason: URI Too Long".
        # For such cases connector tries to use BULK API because it uses POST request and passes properties in the request body.
        bulk_required = properties_length + 2000 > Salesforce.REQUEST_SIZE_LIMITS

        if bulk_required and not rest_required:
            return "bulk"
        elif rest_required and not bulk_required:
            return "rest"
        elif not bulk_required and not rest_required:
            return "rest" if stream_state else "bulk"

    @classmethod
    def generate_streams(
        cls,
        config: Mapping[str, Any],
        stream_objects: Mapping[str, Any],
        sf_object: Salesforce,
        state: Mapping[str, Any] = None,
    ) -> List[Stream]:
        """ "Generates a list of stream by their names. It can be used for different tests too"""
        authenticator = TokenAuthenticator(sf_object.access_token)
        stream_properties = sf_object.generate_schemas(stream_objects)
        streams = []
        for stream_name, sobject_options in stream_objects.items():
            streams_kwargs = {"sobject_options": sobject_options}
            stream_state = state.get(stream_name, {}) if state else {}
            selected_properties = stream_properties.get(stream_name, {}).get("properties", {})

            api_type = cls._get_api_type(stream_name, selected_properties, stream_state)
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

    def streams(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog = None, state: Mapping[str, Any] = None) -> List[Stream]:
        sf = self._get_sf_object(config)
        stream_objects = sf.get_validated_streams(config=config, catalog=catalog)
        streams = self.generate_streams(config, stream_objects, sf, state=state)
        streams.append(Describe(sf_api=sf, catalog=catalog))
        return streams

    def read(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        """
        Overwritten to dynamically receive only those streams that are necessary for reading for significant speed gains
        (Salesforce has a strict API limit on requests).
        """
        connector_state = copy.deepcopy(state or {})
        config, internal_config = split_config(config)
        # get the streams once in case the connector needs to make any queries to generate them
        logger.info("Starting generating streams")
        stream_instances = {s.name: s for s in self.streams(config, catalog=catalog, state=state)}
        logger.info(f"Starting syncing {self.name}")
        self._stream_to_instance_map = stream_instances
        for configured_stream in catalog.streams:
            stream_instance = stream_instances.get(configured_stream.stream.name)
            if not stream_instance:
                raise KeyError(
                    f"The requested stream {configured_stream.stream.name} was not found in the source. Available streams: {stream_instances.keys()}"
                )

            try:
                yield from self._read_stream(
                    logger=logger,
                    stream_instance=stream_instance,
                    configured_stream=configured_stream,
                    connector_state=connector_state,
                    internal_config=internal_config,
                )
            except exceptions.HTTPError as error:
                error_data = error.response.json()[0]
                error_code = error_data.get("errorCode")
                if error.response.status_code == codes.FORBIDDEN and error_code == "REQUEST_LIMIT_EXCEEDED":
                    logger.warn(f"API Call limit is exceeded. Error message: '{error_data.get('message')}'")
                    break  # if got 403 rate limit response, finish the sync with success.
                raise error

            except Exception as e:
                logger.exception(f"Encountered an exception while reading stream {self.name}")
                raise e

        logger.info(f"Finished syncing {self.name}")
