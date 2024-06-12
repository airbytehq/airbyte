#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tyntec_sms import SourceTyntecSms


def run():
    source = SourceTyntecSms()
    launch(source, sys.argv[1:])
