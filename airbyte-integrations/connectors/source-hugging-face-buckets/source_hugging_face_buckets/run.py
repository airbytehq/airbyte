#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_hugging_face_buckets.source import SourceHuggingFaceBuckets


def run():
    source = SourceHuggingFaceBuckets()
    launch(source, sys.argv[1:])