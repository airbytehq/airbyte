#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import importlib
import ipaddress
import logging
import os.path
import socket
import sys
import tempfile
from collections import defaultdict
from functools import wraps
from typing import Any, DefaultDict, Iterable, List, Mapping, Optional
from urllib.parse import urlparse

import requests
from airbyte_cdk.connector import TConfig
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.logger import init_logger
from airbyte_cdk.models import (  # type: ignore [attr-defined]
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateStats,
    ConnectorSpecification,
    FailureType,
    Status,
    Type,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config

# from airbyte_cdk.utils import PrintBuffer, is_cloud_environment, message_utils  # add PrintBuffer back once fixed
from airbyte_cdk.utils import is_cloud_environment, message_utils
from airbyte_cdk.utils.airbyte_secrets_utils import get_secrets, update_secrets
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from orjson import orjson
from requests import PreparedRequest, Response, Session

logger = init_logger("airbyte")

VALID_URL_SCHEMES = ["https"]
CLOUD_DEPLOYMENT_MODE = "cloud"


class AirbyteEntrypoint(object):
    def __init__(self, source: Source):
        init_uncaught_exception_handler(logger)

        # Deployment mode is read when instantiating the entrypoint because it is the common path shared by syncs and connector builder test requests
        if is_cloud_environment():
            _init_internal_request_filter()

        self.source = source
        self.logger = logging.getLogger(f"airbyte.{getattr(source, 'name', '')}")

    @staticmethod
    def parse_args(args: List[str]) -> argparse.Namespace:
        # set up parent parsers
        parent_parser = argparse.ArgumentParser(add_help=False)
        parent_parser.add_argument("--debug", action="store_true", help="enables detailed debug logs related to the sync")
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(title="commands", dest="command")

        # spec
        subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

        # check
        check_parser = subparsers.add_parser("check", help="checks the config can be used to connect", parents=[parent_parser])
        required_check_parser = check_parser.add_argument_group("required named arguments")
        required_check_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

        # discover
        discover_parser = subparsers.add_parser(
            "discover", help="outputs a catalog describing the source's schema", parents=[parent_parser]
        )
        required_discover_parser = discover_parser.add_argument_group("required named arguments")
        required_discover_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

        # read
        read_parser = subparsers.add_parser("read", help="reads the source and outputs messages to STDOUT", parents=[parent_parser])

        read_parser.add_argument("--state", type=str, required=False, help="path to the json-encoded state file")
        required_read_parser = read_parser.add_argument_group("required named arguments")
        required_read_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
        required_read_parser.add_argument(
            "--catalog", type=str, required=True, help="path to the catalog used to determine which data to read"
        )

        return main_parser.parse_args(args)

    def run(self, parsed_args: argparse.Namespace) -> Iterable[str]:
        cmd = parsed_args.command
        if not cmd:
            raise Exception("No command passed")

        if hasattr(parsed_args, "debug") and parsed_args.debug:
            self.logger.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            self.logger.debug("Debug logs enabled")
        else:
            self.logger.setLevel(logging.INFO)

        source_spec: ConnectorSpecification = self.source.spec(self.logger)
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.environ[ENV_REQUEST_CACHE_PATH] = temp_dir  # set this as default directory for request_cache to store *.sqlite files
                if cmd == "spec":
                    message = AirbyteMessage(type=Type.SPEC, spec=source_spec)
                    yield from [
                        self.airbyte_message_to_string(queued_message) for queued_message in self._emit_queued_messages(self.source)
                    ]
                    yield self.airbyte_message_to_string(message)
                else:
                    raw_config = self.source.read_config(parsed_args.config)
                    config = self.source.configure(raw_config, temp_dir)

                    yield from [
                        self.airbyte_message_to_string(queued_message) for queued_message in self._emit_queued_messages(self.source)
                    ]
                    if cmd == "check":
                        yield from map(AirbyteEntrypoint.airbyte_message_to_string, self.check(source_spec, config))
                    elif cmd == "discover":
                        yield from map(AirbyteEntrypoint.airbyte_message_to_string, self.discover(source_spec, config))
                    elif cmd == "read":
                        config_catalog = self.source.read_catalog(parsed_args.catalog)
                        state = self.source.read_state(parsed_args.state)

                        yield from map(AirbyteEntrypoint.airbyte_message_to_string, self.read(source_spec, config, config_catalog, state))
                    else:
                        raise Exception("Unexpected command " + cmd)
        finally:
            yield from [self.airbyte_message_to_string(queued_message) for queued_message in self._emit_queued_messages(self.source)]

    def check(self, source_spec: ConnectorSpecification, config: TConfig) -> Iterable[AirbyteMessage]:
        self.set_up_secret_filter(config, source_spec.connectionSpecification)
        try:
            self.validate_connection(source_spec, config)
        except AirbyteTracedException as traced_exc:
            connection_status = traced_exc.as_connection_status_message()
            # The platform uses the exit code to surface unexpected failures so we raise the exception if the failure type not a config error
            # If the failure is not exceptional, we'll emit a failed connection status message and return
            if traced_exc.failure_type != FailureType.config_error:
                raise traced_exc
            if connection_status:
                yield from self._emit_queued_messages(self.source)
                yield connection_status
                return

        try:
            check_result = self.source.check(self.logger, config)
        except AirbyteTracedException as traced_exc:
            yield traced_exc.as_airbyte_message()
            # The platform uses the exit code to surface unexpected failures so we raise the exception if the failure type not a config error
            # If the failure is not exceptional, we'll emit a failed connection status message and return
            if traced_exc.failure_type != FailureType.config_error:
                raise traced_exc
            else:
                yield AirbyteMessage(
                    type=Type.CONNECTION_STATUS, connectionStatus=AirbyteConnectionStatus(status=Status.FAILED, message=traced_exc.message)
                )
                return
        if check_result.status == Status.SUCCEEDED:
            self.logger.info("Check succeeded")
        else:
            self.logger.error("Check failed")

        yield from self._emit_queued_messages(self.source)
        yield AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=check_result)

    def discover(self, source_spec: ConnectorSpecification, config: TConfig) -> Iterable[AirbyteMessage]:
        self.set_up_secret_filter(config, source_spec.connectionSpecification)
        if self.source.check_config_against_spec:
            self.validate_connection(source_spec, config)
        catalog = self.source.discover(self.logger, config)

        yield from self._emit_queued_messages(self.source)
        yield AirbyteMessage(type=Type.CATALOG, catalog=catalog)

    def read(self, source_spec: ConnectorSpecification, config: TConfig, catalog: Any, state: list[Any]) -> Iterable[AirbyteMessage]:
        self.set_up_secret_filter(config, source_spec.connectionSpecification)
        if self.source.check_config_against_spec:
            self.validate_connection(source_spec, config)

        # The Airbyte protocol dictates that counts be expressed as float/double to better protect against integer overflows
        stream_message_counter: DefaultDict[HashableStreamDescriptor, float] = defaultdict(float)
        for message in self.source.read(self.logger, config, catalog, state):
            yield self.handle_record_counts(message, stream_message_counter)
        for message in self._emit_queued_messages(self.source):
            yield self.handle_record_counts(message, stream_message_counter)

    @staticmethod
    def handle_record_counts(message: AirbyteMessage, stream_message_count: DefaultDict[HashableStreamDescriptor, float]) -> AirbyteMessage:
        match message.type:
            case Type.RECORD:
                stream_message_count[HashableStreamDescriptor(name=message.record.stream, namespace=message.record.namespace)] += 1.0  # type: ignore[union-attr] # record has `stream` and `namespace`
            case Type.STATE:
                stream_descriptor = message_utils.get_stream_descriptor(message)

                # Set record count from the counter onto the state message
                message.state.sourceStats = message.state.sourceStats or AirbyteStateStats()  # type: ignore[union-attr] # state has `sourceStats`
                message.state.sourceStats.recordCount = stream_message_count.get(stream_descriptor, 0.0)  # type: ignore[union-attr] # state has `sourceStats`

                # Reset the counter
                stream_message_count[stream_descriptor] = 0.0
        return message

    @staticmethod
    def validate_connection(source_spec: ConnectorSpecification, config: TConfig) -> None:
        # Remove internal flags from config before validating so
        # jsonschema's additionalProperties flag won't fail the validation
        connector_config, _ = split_config(config)
        check_config_against_spec_or_exit(connector_config, source_spec)

    @staticmethod
    def set_up_secret_filter(config: TConfig, connection_specification: Mapping[str, Any]) -> None:
        # Now that we have the config, we can use it to get a list of ai airbyte_secrets
        # that we should filter in logging to avoid leaking secrets
        config_secrets = get_secrets(connection_specification, config)
        update_secrets(config_secrets)

    @staticmethod
    def airbyte_message_to_string(airbyte_message: AirbyteMessage) -> str:
        return orjson.dumps(AirbyteMessageSerializer.dump(airbyte_message)).decode()  # type: ignore[no-any-return] # orjson.dumps(message).decode() always returns string

    @classmethod
    def extract_state(cls, args: List[str]) -> Optional[Any]:
        parsed_args = cls.parse_args(args)
        if hasattr(parsed_args, "state"):
            return parsed_args.state
        return None

    @classmethod
    def extract_catalog(cls, args: List[str]) -> Optional[Any]:
        parsed_args = cls.parse_args(args)
        if hasattr(parsed_args, "catalog"):
            return parsed_args.catalog
        return None

    @classmethod
    def extract_config(cls, args: List[str]) -> Optional[Any]:
        parsed_args = cls.parse_args(args)
        if hasattr(parsed_args, "config"):
            return parsed_args.config
        return None

    def _emit_queued_messages(self, source: Source) -> Iterable[AirbyteMessage]:
        if hasattr(source, "message_repository") and source.message_repository:
            yield from source.message_repository.consume_queue()
        return


def launch(source: Source, args: List[str]) -> None:
    source_entrypoint = AirbyteEntrypoint(source)
    parsed_args = source_entrypoint.parse_args(args)
    # temporarily removes the PrintBuffer because we're seeing weird print behavior for concurrent syncs
    # Refer to: https://github.com/airbytehq/oncall/issues/6235
    # with PrintBuffer():
    for message in source_entrypoint.run(parsed_args):
        # simply printing is creating issues for concurrent CDK as Python uses different two instructions to print: one for the message and
        # the other for the break line. Adding `\n` to the message ensure that both are printed at the same time
        print(f"{message}\n", end="", flush=True)


def _init_internal_request_filter() -> None:
    """
    Wraps the Python requests library to prevent sending requests to internal URL endpoints.
    """
    wrapped_fn = Session.send

    @wraps(wrapped_fn)
    def filtered_send(self: Any, request: PreparedRequest, **kwargs: Any) -> Response:
        parsed_url = urlparse(request.url)

        if parsed_url.scheme not in VALID_URL_SCHEMES:
            raise requests.exceptions.InvalidSchema(
                "Invalid Protocol Scheme: The endpoint that data is being requested from is using an invalid or insecure "
                + f"protocol {parsed_url.scheme!r}. Valid protocol schemes: {','.join(VALID_URL_SCHEMES)}"
            )

        if not parsed_url.hostname:
            raise requests.exceptions.InvalidURL("Invalid URL specified: The endpoint that data is being requested from is not a valid URL")

        try:
            is_private = _is_private_url(parsed_url.hostname, parsed_url.port)  # type: ignore [arg-type]
            if is_private:
                raise AirbyteTracedException(
                    internal_message=f"Invalid URL endpoint: `{parsed_url.hostname!r}` belongs to a private network",
                    failure_type=FailureType.config_error,
                    message="Invalid URL endpoint: The endpoint that data is being requested from belongs to a private network. Source connectors only support requesting data from public API endpoints.",
                )
        except socket.gaierror as exception:
            # This is a special case where the developer specifies an IP address string that is not formatted correctly like trailing
            # whitespace which will fail the socket IP lookup. This only happens when using IP addresses and not text hostnames.
            # Knowing that this is a request using the requests library, we will mock the exception without calling the lib
            raise requests.exceptions.InvalidURL(f"Invalid URL {parsed_url}: {exception}")

        return wrapped_fn(self, request, **kwargs)

    Session.send = filtered_send  # type: ignore [method-assign]


def _is_private_url(hostname: str, port: int) -> bool:
    """
    Helper method that checks if any of the IP addresses associated with a hostname belong to a private network.
    """
    address_info_entries = socket.getaddrinfo(hostname, port)
    for entry in address_info_entries:
        # getaddrinfo() returns entries in the form of a 5-tuple where the IP is stored as the sockaddr. For IPv4 this
        # is a 2-tuple and for IPv6 it is a 4-tuple, but the address is always the first value of the tuple at 0.
        # See https://docs.python.org/3/library/socket.html#socket.getaddrinfo for more details.
        ip_address = entry[4][0]
        if ipaddress.ip_address(ip_address).is_private:
            return True
    return False


def main() -> None:
    impl_module = os.environ.get("AIRBYTE_IMPL_MODULE", Source.__module__)
    impl_class = os.environ.get("AIRBYTE_IMPL_PATH", Source.__name__)
    module = importlib.import_module(impl_module)
    impl = getattr(module, impl_class)

    # set up and run entrypoint
    source = impl()

    if not isinstance(source, Source):
        raise Exception("Source implementation provided does not implement Source class!")

    launch(source, sys.argv[1:])
