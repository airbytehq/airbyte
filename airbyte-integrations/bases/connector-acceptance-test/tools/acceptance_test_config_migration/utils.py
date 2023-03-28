#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import argparse
from pathlib import Path

from definitions import find_by_name, GA_DEFINITIONS

CONNECTORS_DIRECTORY = "../../../../connectors"


def acceptance_test_config_path(connector_name):
    """Returns the path to a given connector's acceptance-test-config.yml file."""
    return Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-config.yml"


def acceptance_test_docker_sh_path(connector_name):
    return Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-docker.sh"


def add_connectors_param(parser: argparse.ArgumentParser):
    parser.add_argument()


def get_definitions_from_args(args):
    if args.connectors:
        definitions = find_by_name(args.connectors)
    else:
        definitions = GA_DEFINITIONS

    return definitions
