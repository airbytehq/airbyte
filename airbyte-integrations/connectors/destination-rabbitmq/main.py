#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_rabbitmq import DestinationRabbitmq

if __name__ == "__main__":
    DestinationRabbitmq().run(sys.argv[1:])
