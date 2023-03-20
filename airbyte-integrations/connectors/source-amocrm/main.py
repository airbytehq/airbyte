#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amocrm import SourceAmocrm

if __name__ == "__main__":
    source = SourceAmocrm()
    launch(source, sys.argv[1:])
