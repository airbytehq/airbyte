#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""The pipelines package."""
import logging
import os
from typing import Union
from rich.logging import RichHandler

from .helpers import sentry_utils

sentry_utils.initialize()

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# RichHandler does not work great in the CI environment, so we use a StreamHandler instead
logging_handler: Union[RichHandler, logging.StreamHandler] = RichHandler(rich_tracebacks=True) if "CI" not in os.environ else logging.StreamHandler()


logging.basicConfig(
    level=logging.INFO,
    format="%(name)s: %(message)s",
    datefmt="[%X]",
    handlers=[logging_handler],
)

main_logger = logging.getLogger(__name__)
