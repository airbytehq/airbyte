#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stripe import SourceStripe
from freezegun import freeze_time
from datetime import datetime

if __name__ == "__main__":
    now = datetime.now()
    print("now =", now)
    with freeze_time("2023-06-09T00:00:00Z"):
        now = datetime.now()
        print("now2 =", now)
        source = SourceStripe()
        launch(source, sys.argv[1:])
        print(now)
