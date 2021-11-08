#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_intercom import DestinationIntercom

if __name__ == "__main__":
    DestinationIntercom().run(sys.argv[1:])
