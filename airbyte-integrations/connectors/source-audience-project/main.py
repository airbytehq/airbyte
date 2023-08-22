#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_audience_project import SourceAudienceProject

if __name__ == "__main__":
    source = SourceAudienceProject()
    launch(source, sys.argv[1:])
