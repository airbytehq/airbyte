#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import sys

from airbyte_cdk.entrypoint import launch
from source_braintree import SourceBraintree


def run():
    args = sys.argv[1:]
    catalog_path = None
    config_path = None
    state_path = None

    for i in range(len(args) - 1):
        if args[i] == "--catalog":
            catalog_path = args[i + 1]
        elif args[i] == "--config":
            config_path = args[i + 1]
        elif args[i] == "--state":
            state_path = args[i + 1]

    catalog = None
    if catalog_path:
        with open(catalog_path, "r") as f:
            catalog = json.loads(f.read())

    config = None
    if config_path:
        with open(config_path, "r") as f:
            config = json.loads(f.read())

    state = None
    if state_path:
        with open(state_path, "r") as f:
            state = json.loads(f.read())

    source = SourceBraintree(catalog=catalog, config=config, state=state)
    launch(source, args)
