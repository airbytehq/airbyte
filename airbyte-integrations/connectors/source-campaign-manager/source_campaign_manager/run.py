#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceCampaignManager

def run():
    source = SourceCampaignManager()
    launch(source, sys.argv[1:])
