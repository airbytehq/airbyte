#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_amazon_sqs import DestinationAmazonSqs


def run() -> None:
    DestinationAmazonSqs().run(sys.argv[1:])


if __name__ == "__main__":
    run()
