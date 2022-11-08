#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from destination_amazon_sqs import DestinationAmazonSqs

if __name__ == "__main__":
    DestinationAmazonSqs().run(sys.argv[1:])
