# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import sys

# from .source import SourceAmazonGrafana
from source_amazon_grafana.source_amazon_grafana import SourceAmazonGrafana

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceAmazonGrafana()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()