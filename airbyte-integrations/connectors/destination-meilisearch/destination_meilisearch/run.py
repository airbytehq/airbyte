#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_meilisearch import DestinationMeilisearch


def run():
    DestinationMeilisearch().run(sys.argv[1:])
