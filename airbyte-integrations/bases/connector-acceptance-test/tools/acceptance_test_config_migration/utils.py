#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import logging
from pathlib import Path

import definitions

CONNECTORS_DIRECTORY = "../../../../connectors"
MIGRATIONS_FOLDER = "./migrations/"


def acceptance_test_config_path(connector_name):
    """Returns the path to a given connector's acceptance-test-config.yml file."""
    return Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-config.yml"


def acceptance_test_docker_sh_path(connector_name):
    return Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-docker.sh"


def add_dry_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-d",
        "--dry",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether the action performed is a dry run. In the case of a dry run, no git actions will be pushed to the remote.",
    )


def add_allow_alpha_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--allow_alpha",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether to apply the change to alpha connectors, if they are included in the list of connectors.",
    )


def add_allow_beta_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--allow_beta",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether to apply the change to bets connectors, if they are included in the list of connectors.",
    )


def add_connectors_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--connectors", nargs="*", help="A list of connectors (separated by spaces) to run a script on. (default: all connectors)"
    )


def get_valid_definitions_from_args(args):
    if not args.connectors:
        requested_defintions = definitions.ALL_DEFINITIONS
    else:
        requested_defintions = definitions.find_by_name(args.connectors)

    valid_definitions = []
    for definition in requested_defintions:
        connector_technical_name = definitions.get_airbyte_connector_name_from_definition(definition)
        if not definitions.is_airbyte_connector(definition):
            logging.warning(f"Skipping {connector_technical_name} since it's not an airbyte connector.")
        elif not args.allow_beta and definition in definitions.BETA_DEFINITIONS:
            logging.warning(f"Skipping {connector_technical_name} since it's a beta connector. This is configurable via `--allow_beta`")
        elif not args.allow_alpha and definition in definitions.ALPHA_DEFINTIONS:
            logging.warning(f"Skipping {connector_technical_name} since it's an alpha connector. This is configurable via `--allow_alpha`")
        elif definition in definitions.OTHER_DEFINITIONS:
            logging.warning(f"Skipping {connector_technical_name} since it doesn't have a release stage.")
        else:
            valid_definitions.append(definition)

    return valid_definitions
