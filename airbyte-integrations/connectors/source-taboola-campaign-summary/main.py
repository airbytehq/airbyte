#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_taboola_campaign_summary import SourceTaboolaCampaignSummary

if __name__ == "__main__":
    source = SourceTaboolaCampaignSummary()
    launch(source, sys.argv[1:])
