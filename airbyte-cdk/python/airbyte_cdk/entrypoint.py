#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import argparse
import importlib
import logging
import os.path
import sys
import tempfile
from typing import Any, Iterable, List, Mapping

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

logger = init_logger("airbyte")


class AirbyteEntrypoint(object):
    def __init__(self, source: Source):
        init_uncaught_exception_handler(logger)
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

        # todo: add try catch for exceptions with different exit codes
        source_spec: ConnectorSpecification = self.source.spec(self.logger)
        with tempfile.TemporaryDirectory() as temp_dir:
            if cmd == "spec":
                message = AirbyteMessage(type=Type.SPEC, spec=source_spec)
                yield message.json(exclude_unset=True)
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

    def check(self, source_spec: ConnectorSpecification, config: TConfig) -> Iterable[AirbyteMessage]:
        self.set_up_secret_filter(config, source_spec.connectionSpecification)
        try:
            self.validate_connection(source_spec, config)
        except AirbyteTracedException as traced_exc:
            connection_status = traced_exc.as_connection_status_message()
            if connection_status:
                yield connection_status
                return

        check_result = self.source.check(self.logger, config)
        if check_result.status == Status.SUCCEEDED:
            self.logger.info("Check succeeded")
        else:
            self.logger.error("Check failed")

        yield AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=check_result)

    def discover(self, source_spec: ConnectorSpecification, config: TConfig) -> Iterable[AirbyteMessage]:
        self.set_up_secret_filter(config, source_spec.connectionSpecification)
        if self.source.check_config_against_spec:
            self.validate_connection(source_spec, config)
        catalog = self.source.discover(self.logger, config)
        yield AirbyteMessage(type=Type.CATALOG, catalog=catalog)

    def read(self, source_spec: ConnectorSpecification, config: TConfig, catalog: TCatalog, state: TState) -> Iterable[AirbyteMessage]:
        self.set_up_secret_filter(config, source_spec.connectionSpecification)
        if self.source.check_config_against_spec:
            self.validate_connection(source_spec, config)

        yield from self.source.read(self.logger, config, catalog, state)

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


def launch(source: Source, args: List[str]):
    source_entrypoint = AirbyteEntrypoint(source)
    parsed_args = source_entrypoint.parse_args(args)
    for message in source_entrypoint.run(parsed_args):
        print(message)


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
