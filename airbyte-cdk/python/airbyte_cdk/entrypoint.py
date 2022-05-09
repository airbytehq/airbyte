#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import argparse
import importlib
import logging
import os.path
import sys
import tempfile
from typing import Any, Dict, Iterable, List

from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.logger import init_logger
from airbyte_cdk.models import AirbyteMessage, Status, Type
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, get_secret_values, split_config
from airbyte_cdk.sources.utils.sentry import AirbyteSentry
from airbyte_cdk.utils.airbyte_secrets_utils import get_secrets, update_secrets

logger = init_logger("airbyte")
init_uncaught_exception_handler(logger)


class AirbyteEntrypoint(object):
    def __init__(self, source: Source):
        self.source = source
        self.logger = logging.getLogger(f"airbyte.{getattr(source, 'name', '')}")

    @staticmethod
    def parse_args(args: List[str]) -> argparse.Namespace:
        # set up parent parsers
        parent_parser = argparse.ArgumentParser(add_help=False)
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

    def configure_sentry(self, spec_schema: Dict[str, Any], parsed_args: argparse.Namespace):
        secret_values = []
        if "config" in parsed_args:
            config = self.source.read_config(parsed_args.config)
            secret_values = get_secret_values(spec_schema, config)
        source_name = self.source.__module__.split(".")[0]
        source_name = source_name.split("_", 1)[-1]
        AirbyteSentry.init(source_tag=source_name, secret_values=secret_values)

    def run(self, parsed_args: argparse.Namespace) -> Iterable[str]:
        cmd = parsed_args.command
        if not cmd:
            raise Exception("No command passed")

        # todo: add try catch for exceptions with different exit codes
        source_spec: ConnectorSpecification = self.source.spec(self.logger)
        self.configure_sentry(source_spec.connectionSpecification, parsed_args)
        with tempfile.TemporaryDirectory() as temp_dir:
            if cmd == "spec":
                message = AirbyteMessage(type=Type.SPEC, spec=source_spec)
                yield message.json(exclude_unset=True)
            else:
                raw_config = self.source.read_config(parsed_args.config)
                config = self.source.configure(raw_config, temp_dir)

                # Now that we have the config, we can use it to get a list of ai airbyte_secrets
                # that we should filter in logging to avoid leaking secrets
                config_secrets = get_secrets(self.source, config, self.logger)
                update_secrets(config_secrets)

                # Remove internal flags from config before validating so
                # jsonschema's additionalProperties flag wont fail the validation
                config, internal_config = split_config(config)
                if self.source.check_config_against_spec or cmd == "check":
                    check_config_against_spec_or_exit(config, source_spec)
                # Put internal flags back to config dict
                config.update(internal_config.dict())

                if cmd == "check":
                    check_result = self.source.check(self.logger, config)
                    if check_result.status == Status.SUCCEEDED:
                        self.logger.info("Check succeeded")
                    else:
                        self.logger.error("Check failed")

                    output_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=check_result).json(exclude_unset=True)
                    yield output_message
                elif cmd == "discover":
                    catalog = self.source.discover(self.logger, config)
                    yield AirbyteMessage(type=Type.CATALOG, catalog=catalog).json(exclude_unset=True)
                elif cmd == "read":
                    config_catalog = self.source.read_catalog(parsed_args.catalog)
                    state = self.source.read_state(parsed_args.state)
                    generator = self.source.read(self.logger, config, config_catalog, state)
                    for message in generator:
                        yield message.json(exclude_unset=True)
                else:
                    raise Exception("Unexpected command " + cmd)


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
