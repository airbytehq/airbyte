#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_langchain import DestinationLangchain

if __name__ == "__main__":
    DestinationLangchain().run(sys.argv[1:])
