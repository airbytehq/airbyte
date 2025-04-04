#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_weaviate import DestinationWeaviate


if __name__ == "__main__":
    DestinationWeaviate().run(sys.argv[1:])
