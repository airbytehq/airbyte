#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_twilio_taskrouter import SourceTwilioTaskrouter

if __name__ == "__main__":
    source = SourceTwilioTaskrouter()
    launch(source, sys.argv[1:])
