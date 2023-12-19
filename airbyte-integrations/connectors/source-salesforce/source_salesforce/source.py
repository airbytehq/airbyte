#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, Level, SyncMode
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from dateutil.relativedelta import relativedelta
from requests import codes, exceptions  # type: ignore[import]

from .api import PARENT_SALESFORCE_OBJECTS, UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS, UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .streams import (
    BulkIncrementalSalesforceStream,
    BulkSalesforceStream,
    BulkSalesforceSubStream,
    Describe,
    IncrementalRestSalesforceStream,
    RestSalesforceStream,
    RestSalesforceSubStream,
)

_DEFAULT_CONCURRENCY = 10
_MAX_CONCURRENCY = 10
logger = logging.getLogger("airbyte")


class AirbyteStopSync(AirbyteTracedException):
    pass


class SourceSalesforce(ConcurrentSourceAdapter):
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    START_DATE_OFFSET_IN_YEARS = 2
    MAX_WORKERS = 5

    message_repository = InMemoryMessageRepository(Level(AirbyteLogFormatter.level_mapping[logger.level]))

    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], **kwargs):
        if config:
            concurrency_level = min(config.get("num_workers", _DEFAULT_CONCURRENCY), _MAX_CONCURRENCY)
        else:
            concurrency_level = _DEFAULT_CONCURRENCY
        logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")
        concurrent_source = ConcurrentSource.create(
            concurrency_level, concurrency_level // 2, logger, self._slice_logger, self.message_repository
        )
        super().__init__(concurrent_source)
        self.catalog = catalog

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
    def _get_api_type(cls, stream_name: str, json_schema: Mapping[str, Any], force_use_bulk_api: bool) -> str:
        """Get proper API type: rest or bulk"""
        # Salesforce BULK API currently does not support loading fields with data type base64 and compound data
        properties = json_schema.get("properties", {})
        properties_not_supported_by_bulk = {
            key: value for key, value in properties.items() if value.get("format") == "base64" or "object" in value["type"]
        }
        rest_only = stream_name in UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS
        if rest_only:
            logger.warning(f"BULK API is not supported for stream: {stream_name}")
            return "rest"
        if force_use_bulk_api and properties_not_supported_by_bulk:
            logger.warning(
                f"Following properties will be excluded from stream: {stream_name} due to BULK API limitations: {list(properties_not_supported_by_bulk)}"
            )
            return "bulk"
        if properties_not_supported_by_bulk:
            return "rest"
        return "bulk"

    @classmethod
    def _get_stream_type(cls, stream_name: str, api_type: str):
        """Get proper stream class: full_refresh, incremental or substream

        SubStreams (like ContentDocumentLink) do not support incremental sync because of query restrictions, look here:
        https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_contentdocumentlink.htm
        """
        parent_name = PARENT_SALESFORCE_OBJECTS.get(stream_name, {}).get("parent_name")
        if api_type == "rest":
            full_refresh = RestSalesforceSubStream if parent_name else RestSalesforceStream
            incremental = IncrementalRestSalesforceStream
        elif api_type == "bulk":
            full_refresh = BulkSalesforceSubStream if parent_name else BulkSalesforceStream
            incremental = BulkIncrementalSalesforceStream
        else:
            raise Exception(f"Stream {stream_name} cannot be processed by REST or BULK API.")
        return full_refresh, incremental

    @classmethod
    def prepare_stream(cls, stream_name: str, json_schema, sobject_options, sf_object, authenticator, config):
        """Choose proper stream class: syncMode(full_refresh/incremental), API type(Rest/Bulk), SubStream"""
        pk, replication_key = sf_object.get_pk_and_replication_key(json_schema)
        stream_kwargs = {
            "stream_name": stream_name,
            "schema": json_schema,
            "pk": pk,
            "sobject_options": sobject_options,
            "sf_api": sf_object,
            "authenticator": authenticator,
            "start_date": config.get("start_date"),
        }

        api_type = cls._get_api_type(stream_name, json_schema, config.get("force_use_bulk_api", False))
        full_refresh, incremental = cls._get_stream_type(stream_name, api_type)
        if replication_key and stream_name not in UNSUPPORTED_FILTERING_STREAMS:
            stream_class = incremental
            stream_kwargs["replication_key"] = replication_key
        else:
            stream_class = full_refresh

        return stream_class, stream_kwargs

    @classmethod
    def generate_streams(
        cls,
        config: Mapping[str, Any],
        stream_objects: Mapping[str, Any],
        sf_object: Salesforce,
    ) -> List[Stream]:
        """Generates a list of stream by their names. It can be used for different tests too"""
        authenticator = TokenAuthenticator(sf_object.access_token)
        schemas = sf_object.generate_schemas(stream_objects)
        default_args = [sf_object, authenticator, config]
        streams = []
        for stream_name, sobject_options in stream_objects.items():
            json_schema = schemas.get(stream_name, {})

            stream_class, kwargs = cls.prepare_stream(stream_name, json_schema, sobject_options, *default_args)

            parent_name = PARENT_SALESFORCE_OBJECTS.get(stream_name, {}).get("parent_name")
            if parent_name:
                # get minimal schema required for getting proper class name full_refresh/incremental, rest/bulk
                parent_schema = PARENT_SALESFORCE_OBJECTS.get(stream_name, {}).get("schema_minimal")
                parent_class, parent_kwargs = cls.prepare_stream(parent_name, parent_schema, sobject_options, *default_args)
                kwargs["parent"] = parent_class(**parent_kwargs)

            stream = stream_class(**kwargs)

            api_type = cls._get_api_type(stream_name, json_schema, config.get("force_use_bulk_api", False))
            if api_type == "rest" and not stream.primary_key and stream.too_many_properties:
                logger.warning(
                    f"Can not instantiate stream {stream_name}. It is not supported by the BULK API and can not be "
                    "implemented via REST because the number of its properties exceeds the limit and it lacks a primary key."
                )
                continue
            streams.append(stream)
        return streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if not config.get("start_date"):
            config["start_date"] = (datetime.now() - relativedelta(years=self.START_DATE_OFFSET_IN_YEARS)).strftime(self.DATETIME_FORMAT)
        sf = self._get_sf_object(config)
        stream_objects = sf.get_validated_streams(config=config, catalog=self.catalog)
        streams = self.generate_streams(config, stream_objects, sf)
        streams.append(Describe(sf_api=sf, catalog=self.catalog))
        # TODO: incorporate state & ConcurrentCursor when we support incremental
        configured_streams = []
        for stream in streams:
            sync_mode = self._get_sync_mode_from_catalog(stream)
            if sync_mode == SyncMode.full_refresh:
                configured_streams.append(StreamFacade.create_from_stream(stream, self, logger, None, NoopCursor()))
            else:
                configured_streams.append(stream)
        return configured_streams

    def _get_sync_mode_from_catalog(self, stream: Stream) -> Optional[SyncMode]:
        if self.catalog:
            for catalog_stream in self.catalog.streams:
                if stream.name == catalog_stream.stream.name:
                    return catalog_stream.sync_mode
        return None

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
