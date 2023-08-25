#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_sonar_cloud import SourceSonarCloud

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceSonarCloud()
    launch(source, sys.argv[1:])
