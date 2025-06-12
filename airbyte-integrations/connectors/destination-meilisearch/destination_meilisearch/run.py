#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from destination_meilisearch import DestinationMeilisearch

from airbyte_cdk.entrypoint import launch


def run():
    source = DestinationMeilisearch()
    launch(source, sys.argv[1:])
