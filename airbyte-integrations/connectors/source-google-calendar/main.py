#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_calendar import SourceGoogleCalendar

if __name__ == "__main__":
    source = SourceGoogleCalendar()
    launch(source, sys.argv[1:])
