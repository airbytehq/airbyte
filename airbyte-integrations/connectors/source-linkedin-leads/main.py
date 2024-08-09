#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linkedin_leads import SourceLinkedinLeads

if __name__ == "__main__":
    source = SourceLinkedinLeads()
    launch(source, sys.argv[1:])
