#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from destination_hugging_face_buckets.destination import DestinationHuggingFaceBuckets


def run():
    """Run the destination with sys.argv"""
    destination = DestinationHuggingFaceBuckets()
    destination.run(sys.argv[1:])


if __name__ == "__main__":
    run()