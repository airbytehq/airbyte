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
from functools import wraps
from typing import Any, Iterable, List, Mapping
from urllib.parse import urlparse

from airbyte_cdk.connector import TConfig
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.logger import init_logger
from airbyte_cdk.models import AirbyteMessage, Status, Type
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.source import TCatalog, TState
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config
from airbyte_cdk.utils.airbyte_secrets_utils import get_secrets, update_secrets
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from requests import Session

logger = init_logger("airbyte")

VALID_URL_SCHEMES = ["https"]
CLOUD_DEPLOYMENT_MODE = "cloud"


class AirbyteEntrypoint(object):
    def __init__(self, source: Source):
        init_uncaught_exception_handler(logger)

        # DEPLOYMENT_MODE is read when instantiating the entrypoint because it is the common path shared by syncs and connector
        # builder test requests
        deployment_mode = os.environ.get("DEPLOYMENT_MODE", "")
        if deployment_mode.casefold() == CLOUD_DEPLOYMENT_MODE:
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
            self.logger.debug("Debug logs enabled")
        else:
            self.logger.setLevel(logging.INFO)

        source_spec: ConnectorSpecification = self.source.spec(self.logger)
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                if cmd == "spec":
                    message = AirbyteMessage(type=Type.SPEC, spec=source_spec)
                    yield from [
                        self.airbyte_message_to_string(queued_message) for queued_message in self._emit_queued_messages(self.source)
                    ]
                    yield self.airbyte_message_to_string(message)
                else:
                    raw_config = self.source.read_config(parsed_args.config)
                    config = self.source.configure(raw_config, temp_dir)

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
            if connection_status:
                yield from self._emit_queued_messages(self.source)
                yield connection_status
                return

        check_result = self.source.check(self.logger, config)
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

    def read(self, source_spec: ConnectorSpecification, config: TConfig, catalog: TCatalog, state: TState) -> Iterable[AirbyteMessage]:
        self.set_up_secret_filter(config, source_spec.connectionSpecification)
        if self.source.check_config_against_spec:
            self.validate_connection(source_spec, config)

        yield from self.source.read(self.logger, config, catalog, state)
        yield from self._emit_queued_messages(self.source)

    @staticmethod
    def validate_connection(source_spec: ConnectorSpecification, config: Mapping[str, Any]) -> None:
        # Remove internal flags from config before validating so
        # jsonschema's additionalProperties flag won't fail the validation
        connector_config, _ = split_config(config)
        check_config_against_spec_or_exit(connector_config, source_spec)

    @staticmethod
    def set_up_secret_filter(config, connection_specification: Mapping[str, Any]):
        # Now that we have the config, we can use it to get a list of ai airbyte_secrets
        # that we should filter in logging to avoid leaking secrets
        config_secrets = get_secrets(connection_specification, config)
        update_secrets(config_secrets)

    @staticmethod
    def airbyte_message_to_string(airbyte_message: AirbyteMessage) -> str:
        return airbyte_message.json(exclude_unset=True)

    def _emit_queued_messages(self, source) -> Iterable[AirbyteMessage]:
        if hasattr(source, "message_repository") and source.message_repository:
            yield from source.message_repository.consume_queue()
        return


def launch(source: Source, args: List[str]):
    source_entrypoint = AirbyteEntrypoint(source)
    parsed_args = source_entrypoint.parse_args(args)
    for message in source_entrypoint.run(parsed_args):
        print(message)


def _init_internal_request_filter():
    """
    Wraps the Python requests library to prevent sending requests to internal URL endpoints.
    """
    wrapped_fn = Session.send

    @wraps(wrapped_fn)
    def filtered_send(self, request, **kwargs):
        parsed_url = urlparse(request.url)

        if parsed_url.scheme not in VALID_URL_SCHEMES:
            raise ValueError(
                "Invalid Protocol Scheme: The endpoint that data is being requested from is using an invalid or insecure "
                + f"protocol {parsed_url.scheme}. Valid protocol schemes: {','.join(VALID_URL_SCHEMES)}"
            )

        if not parsed_url.hostname:
            raise ValueError("Invalid URL specified: The endpoint that data is being requested from is not a valid URL")

        try:
            is_private = _is_private_url(parsed_url.hostname, parsed_url.port)
            if is_private:
                raise ValueError(
                    "Invalid URL endpoint: The endpoint that data is being requested from belongs to a private network. Source "
                    + "connectors only support requesting data from public API endpoints."
                )
        except socket.gaierror:
            # This is a special case where the developer specifies an IP address string that is not formatted correctly like trailing
            # whitespace which will fail the socket IP lookup. This only happens when using IP addresses and not text hostnames.
            raise ValueError(f"Invalid hostname or IP address '{parsed_url.hostname}' specified.")

        return wrapped_fn(self, request, **kwargs)

    Session.send = filtered_send


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


def main():
    impl_module = os.environ.get("AIRBYTE_IMPL_MODULE", Source.__module__)
    impl_class = os.environ.get("AIRBYTE_IMPL_PATH", Source.__name__)
    module = importlib.import_module(impl_module)
    impl = getattr(module, impl_class)

    # set up and run entrypoint
    source = impl()

    if not isinstance(source, Source):
        raise Exception("Source implementation provided does not implement Source class!")

    launch(source, sys.argv[1:])
