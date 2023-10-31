#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_active_campaign import SourceActiveCampaign

if __name__ == "__main__":
    source = SourceActiveCampaign()
    launch(source, sys.argv[1:])
