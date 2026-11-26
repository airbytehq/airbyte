#!/usr/bin/env python3
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Run function for the Hugging Face Datasets source connector."""

import sys

from airbyte_cdk.entrypoint import launch
from source_hugging_face_datasets.source import SourceHuggingFaceDatasets


def run():
    source = SourceHuggingFaceDatasets()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
