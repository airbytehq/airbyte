#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tyntec_sms import SourceTyntecSms

if __name__ == "__main__":
    source = SourceTyntecSms()
    launch(source, sys.argv[1:])
