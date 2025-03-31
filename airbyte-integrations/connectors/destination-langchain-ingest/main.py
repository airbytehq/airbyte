#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from destination_langchain_ingest import DestinationLangchainIngest

if __name__ == "__main__":
    DestinationLangchainIngest().run(sys.argv[1:])
