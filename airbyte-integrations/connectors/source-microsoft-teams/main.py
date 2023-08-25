#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_microsoft_teams import SourceMicrosoftTeams

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceMicrosoftTeams()
    launch(source, sys.argv[1:])
