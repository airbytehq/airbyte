#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_tyntec_sms import SourceTyntecSms

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceTyntecSms()
    launch(source, sys.argv[1:])
