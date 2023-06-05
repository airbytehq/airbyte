#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
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
from dateutil.relativedelta import relativedelta
from requests import codes, exceptions  # type: ignore[import]

from .api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS, UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .streams import BulkIncrementalSalesforceStream, BulkSalesforceStream, Describe, IncrementalRestSalesforceStream, RestSalesforceStream


class AirbyteStopSync(AirbyteTracedException):
    pass


class SourceSalesforce(AbstractSource):
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    START_DATE_OFFSET_IN_YEARS = 2

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
        rest_required = stream_name in UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS or properties_not_supported_by_bulk
        if rest_required:
            return "rest"
        return "bulk"

    @classmethod
    def generate_streams(
        cls,
        config: Mapping[str, Any],
        stream_objects: Mapping[str, Any],
        sf_object: Salesforce,
    ) -> List[Stream]:
        """ "Generates a list of stream by their names. It can be used for different tests too"""
        logger = logging.getLogger()
        authenticator = TokenAuthenticator(sf_object.access_token)
        stream_properties = sf_object.generate_schemas(stream_objects)
        streams = []
        for stream_name, sobject_options in stream_objects.items():
            streams_kwargs = {"sobject_options": sobject_options}
            selected_properties = stream_properties.get(stream_name, {}).get("properties", {})

            api_type = cls._get_api_type(stream_name, selected_properties)
            if api_type == "rest":
                full_refresh, incremental = RestSalesforceStream, IncrementalRestSalesforceStream
            elif api_type == "bulk":
                full_refresh, incremental = BulkSalesforceStream, BulkIncrementalSalesforceStream
            else:
                raise Exception(f"Stream {stream_name} cannot be processed by REST or BULK API.")

            json_schema = stream_properties.get(stream_name, {})
            pk, replication_key = sf_object.get_pk_and_replication_key(json_schema)
            streams_kwargs.update(dict(sf_api=sf_object, pk=pk, stream_name=stream_name, schema=json_schema, authenticator=authenticator))
            if replication_key and stream_name not in UNSUPPORTED_FILTERING_STREAMS:
                start_date = config.get(
                    "start_date", (datetime.now() - relativedelta(years=cls.START_DATE_OFFSET_IN_YEARS)).strftime(cls.DATETIME_FORMAT)
                )
                stream = incremental(**streams_kwargs, replication_key=replication_key, start_date=start_date)
            else:
                stream = full_refresh(**streams_kwargs)
            if api_type == "rest" and not stream.primary_key and stream.too_many_properties:
                logger.warning(
                    f"Can not instantiate stream {stream_name}. "
                    f"It is not supported by the BULK API and can not be implemented via REST because the number of its properties "
                    f"exceeds the limit and it lacks a primary key."
                )
                continue
            streams.append(stream)
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
            url = error.response.url
            if error.response.status_code == codes.FORBIDDEN and error_code == "REQUEST_LIMIT_EXCEEDED":
                logger.warning(f"API Call {url} limit is exceeded. Error message: '{error_data.get('message')}'")
                raise AirbyteStopSync()  # if got 403 rate limit response, finish the sync with success.
            raise error
