#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_microsoft_teams import SourceMicrosoftTeams

if __name__ == "__main__":
    source = SourceMicrosoftTeams()
    launch(source, sys.argv[1:])
