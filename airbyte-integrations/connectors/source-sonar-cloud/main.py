#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sonar_cloud import SourceSonarCloud

if __name__ == "__main__":
    source = SourceSonarCloud()
    launch(source, sys.argv[1:])
