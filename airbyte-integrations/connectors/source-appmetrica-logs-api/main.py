#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import sys

from airbyte_cdk.entrypoint import launch
from source_appmetrica_logs_api import SourceAppmetricaLogsApi
import shutil

logger = logging.getLogger("airbyte")

if __name__ == "__main__":
    logger.info("Clean output folder on start")
    shutil.rmtree("./output", ignore_errors=True)
    try:
        source = SourceAppmetricaLogsApi()
        launch(source, sys.argv[1:])
    except:
        raise
    finally:
        logger.info("Finally clean ouput folder")
        shutil.rmtree("./output", ignore_errors=True)
