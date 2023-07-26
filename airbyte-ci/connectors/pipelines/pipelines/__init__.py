#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""The pipelines package."""
import logging
import os
import sentry_sdk

from rich.logging import RichHandler

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging_handlers = [RichHandler(rich_tracebacks=True)]
if "CI" in os.environ:
    # RichHandler does not work great in the CI
    logging_handlers = [logging.StreamHandler()]

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=logging_handlers)

main_logger = logging.getLogger(__name__)

sentry_sdk.init(
    dsn="https://f2e9aeb6b24b4024b09679201c7f563e@o1009025.ingest.sentry.io/4505596642983936",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)
