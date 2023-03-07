#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_adaptive_insights import SourceAdaptiveInsights

if __name__ == "__main__":
    source = SourceAdaptiveInsights()
    launch(source, sys.argv[1:])
