#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from destination_hugging_face_datasets.destination import DestinationHuggingFaceDatasets


def run():
    """Run the destination with sys.argv."""
    destination = DestinationHuggingFaceDatasets()
    destination.run(sys.argv[1:])


if __name__ == "__main__":
    run()
