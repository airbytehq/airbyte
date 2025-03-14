#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import argparse
import logging
from typing import List

from airbyte_cdk.exception_handler import init_uncaught_exception_handler


_LOGGER = logging.getLogger("airbyte")

import sys

from destination_cobra import DestinationCobra


def _parse_args(args: List[str]) -> argparse.Namespace:
    """
    FIXME copied from destination.py. We should do a CDK change to make this static

    TODO: A change was done to support debug logs as well.
    """

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

    # write
    write_parser = subparsers.add_parser("write", help="Writes data to the destination", parents=[parent_parser])
    write_required = write_parser.add_argument_group("required named arguments")
    write_required.add_argument("--config", type=str, required=True, help="path to the JSON configuration file")
    write_required.add_argument("--catalog", type=str, required=True, help="path to the configured catalog JSON file")

    parsed_args = main_parser.parse_args(args)
    cmd = parsed_args.command
    if not cmd:
        raise Exception("No command entered. ")
    elif cmd not in ["spec", "check", "write"]:
        # This is technically dead code since parse_args() would fail if this was the case
        # But it's non-obvious enough to warrant placing it here anyways
        raise Exception(f"Unknown command entered: {cmd}")

    return parsed_args


if __name__ == "__main__":
    init_uncaught_exception_handler(_LOGGER)

    argv = sys.argv[1:]
    args = _parse_args(argv)
    if args.debug:
        _LOGGER.setLevel(logging.DEBUG)

    if args.command == "spec":
        destination = DestinationCobra.for_spec(_LOGGER)
    else:
        config = DestinationCobra.read_config(config_path=args.config)
        destination = DestinationCobra.create(config, _LOGGER)

    if "--debug" in argv:
        argv.remove("--debug")
    destination.run(argv)
