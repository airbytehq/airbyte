#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_meilisearch import DestinationMeilisearch

if __name__ == "__main__":
    DestinationMeilisearch().run(sys.argv[1:])
