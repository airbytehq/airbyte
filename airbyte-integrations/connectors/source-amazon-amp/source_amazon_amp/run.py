# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import sys

# from .source import SourceAmazonAmp
from source_amazon_amp.source_amazon_amp import SourceAmazonAmp

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceAmazonAmp()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
