#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from datetime import datetime
from typing import Any, Iterable, Mapping, Optional

from requests.auth import AuthBase

from airbyte_cdk import (
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteTracedException,
    ConfiguredAirbyteCatalog,
    DeclarativeOauth2Authenticator,
    FailureType,
    Level,
    Status,
    Type,
)
from airbyte_cdk.destinations import Destination
from airbyte_cdk.sources.streams.http import HttpClient
from destination_cobra.api.processor import Operation, RecordProcessor


_DO_NOT_PRINT_RECORD_IN_ERROR_MESSAGES = False


class DestinationCobra(Destination):
    @classmethod
    def for_spec(cls, logger: logging.Logger) -> Destination:
        return cls(None, {}, [], logger, _DO_NOT_PRINT_RECORD_IN_ERROR_MESSAGES)

    @classmethod
    def create(cls, config: Mapping[str, Any], logger: logging.Logger) -> Destination:
        if not config:
            return cls.for_spec(logger)
        elif not config.get("stream_mappings", None):
            raise AirbyteTracedException(message="table mapping was not provided in configuration", failure_type=FailureType.config_error)

        no_expiration = (
            datetime.max
        )  # Salesforce does not return time expiry time and we will assume for now that as long as we use it, the token will be available
        return cls(
            DeclarativeOauth2Authenticator(
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                refresh_token=config["refresh_token"],
                token_expiry_date=no_expiration.strftime("%Y-%m-%d %H:%M:%S"),
                token_refresh_endpoint=f"https://{'test' if config.get('is_sandbox', False) else 'login'}.salesforce.com/services/oauth2/token",
                config=config,
                parameters={},
            ),
            {
                mapping["source_stream"]: Operation(mapping["destination_table"], mapping["update_mode"], mapping.get("upsert_key", None))
                for mapping in config["stream_mappings"]
            },
            config.get("stream_order", None),
            logger,
            config.get("print_record_content_on_error", _DO_NOT_PRINT_RECORD_IN_ERROR_MESSAGES),
        )

    def __init__(
        self,
        authenticator: Optional[AuthBase],
        source_to_destination_operation_mapping: Mapping[str, Operation],
        stream_order: Optional[Iterable[str]],
        logger: logging.Logger,
        print_record_content_on_error: bool,
    ):
        self._http_client = HttpClient(
            name="destination-cobra",
            logger=logger,
            authenticator=authenticator,
        )
        self.__url_base: Optional[str] = None
        self._authenticator = authenticator
        self._source_to_destination_operation_mapping = source_to_destination_operation_mapping
        self._stream_order = stream_order
        self._logger = logger
        self._print_record_content_on_error = print_record_content_on_error

    @property
    def _url_base(self) -> str:
        """
        Utility method to cache the URL base and avoid making multiple requests to Salesforce. We can't run this in __init__ because methods like `spec` don't provide a config
        """
        if self.__url_base is None:
            try:
                self.__url_base = self._authenticator._make_handled_request()[
                    "instance_url"
                ]  # FIXME we should find a way not to depend on the private method
            except Exception as e:
                raise AirbyteTracedException(message=f"Failed to authenticate to Salesforce: {e}", failure_type=FailureType.config_error)
        return self.__url_base

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Limits:
            150 MB per job
            (ignoring because of next criteria) The total size of the unzipped content can’t exceed 20 MB.
            Maximum number of characters for all the data in a batch: 10,000,000
            Maximum number of records in a batch: 10,000

            Maximum number of characters in a record: 400,000
            Maximum number of fields in a record: 5,000
            Maximum number of characters in a field: 131072
        """
        record_processor = self._instantiate_record_processor()

        for message in input_messages:
            self._logger.debug(f"Processing message: {message}")
            if message.type == Type.RECORD:
                record_processor.process(message.record)

        record_processor.flush()

        yield AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Sync completed"))

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            _, response = self._http_client.send_request(
                http_method="GET",
                url=f"{self._url_base}/services/data/v62.0/sobjects/Contact/describe/",
                request_kwargs={},
            )
            if response.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            return AirbyteConnectionStatus(status=Status.FAILED)  # FIXME provide info as to why it failed
        except AirbyteTracedException as traced_exception:
            return AirbyteConnectionStatus(status=Status.FAILED, message=traced_exception.message)
        except Exception as exception:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(exception))

    def _instantiate_record_processor(self) -> RecordProcessor:
        """
        We don't do that during __init__ because some commands like SPEC do not have all the information
        """
        return RecordProcessor(
            self._http_client,
            self._url_base,
            self._source_to_destination_operation_mapping,
            self._stream_order,
            print_record_content_on_error=self._print_record_content_on_error,
        )
