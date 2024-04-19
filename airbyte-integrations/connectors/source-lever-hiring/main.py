#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch

from source_lever_hiring import SourceLeverHiring
from source_lever_hiring.run import run

if __name__ == "__main__":
    run()
