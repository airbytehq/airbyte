#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from destination_lime_crm import DestinationLimeCrm
import json
import pathlib
import sys
import logging
from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
    AirbyteMessage,
)


logger = logging.getLogger()

# Ensure logs are printed to stdout
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def integration_test():
    with open("integration_tests/config.json", "r") as file:
        config = json.load(file)

    if not pathlib.Path("integration_tests/secret_api_key").exists():
        print("Please provide a integration_tests/secret_api_key file")
        sys.exit(1)

    with open("integration_tests/secret_api_key", "r") as file:
        secret_api_key = file.read().strip()

    config["api_key"] = secret_api_key

    dest = DestinationLimeCrm()

    input_messages, configured_catalog = None, None
    with open("integration_tests/catalog.json", "r") as file:
        configured_catalog = json.load(file)

    with open("integration_tests/input_messages.jsonl", "r") as file:
        input_messages = [x.strip() for x in file.readlines()]

    configured_catalog = ConfiguredAirbyteCatalog.parse_obj(configured_catalog)
    input_messages = (
        AirbyteMessage.parse_obj(json.loads(x)) for x in input_messages
    )

    messages = dest.write(
        config=config,
        configured_catalog=configured_catalog,
        input_messages=input_messages
    )

    [_ for _ in messages]

    print("Integration test passed")


if __name__ == "__main__":
    integration_test()
