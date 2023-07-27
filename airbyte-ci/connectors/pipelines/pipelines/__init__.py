#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""The pipelines package."""
import logging
import os
import sentry_sdk
import importlib.metadata

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

if os.environ.get("SENTRY_DSN", None):
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"], 
        release=f"pipelines@{importlib.metadata.version('pipelines')}"
    )