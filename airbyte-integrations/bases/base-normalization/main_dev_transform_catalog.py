#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging

from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from normalization.transform_catalog.transform import main

if __name__ == "__main__":
    init_uncaught_exception_handler(logging.getLogger("airbyte"))
    try:
        main()
    except Exception as e:
        msg = (
            "Something went wrong while normalizing the data moved in this sync "
            + "(failed to transform catalog into dbt project). See the logs for more details."
        )
        raise AirbyteTracedException.from_exception(e, message=msg)
