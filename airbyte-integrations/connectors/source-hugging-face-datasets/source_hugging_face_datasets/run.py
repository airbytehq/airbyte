#!/usr/bin/env python3
"""Run function for the Hugging Face Datasets source connector."""

import sys

from airbyte_cdk.entrypoint import launch
from source_hugging_face_datasets.source import SourceHuggingFaceDatasets


def main() -> int:
    """Run the connector."""
    source = SourceHuggingFaceDatasets()
    launch(source, sys.argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(main())