#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_twilio_taskrouter import SourceTwilioTaskrouter


def run():
    source = SourceTwilioTaskrouter()
    launch(source, sys.argv[1:])
