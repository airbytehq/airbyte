#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailjet_sms import SourceMailjetSms


def run():
    source = SourceMailjetSms()
    launch(source, sys.argv[1:])
