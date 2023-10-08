#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_source_freshdesk_yaml import SourceSourceFreshdeskYaml

if __name__ == "__main__":
    source = SourceSourceFreshdeskYaml()
    launch(source, sys.argv[1:])
