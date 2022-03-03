#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_jenkins_blue import SourceJenkinsBlue

if __name__ == "__main__":
    source = SourceJenkinsBlue()
    launch(source, sys.argv[1:])
