#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
import os

import sentry_sdk

sentry_logger = logging.getLogger("sentry")


def setup_sentry():
    """
    Setup the sentry SDK if SENTRY_DSN is defined for the environment.

    Additionally TRACES_SAMPLE_RATE can be set 0-1 otherwise will default to 0.
    """
    from sentry_sdk.integrations.argv import ArgvIntegration
    from sentry_sdk.integrations.atexit import AtexitIntegration
    from sentry_sdk.integrations.dedupe import DedupeIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger
    from sentry_sdk.integrations.modules import ModulesIntegration
    from sentry_sdk.integrations.stdlib import StdlibIntegration

    # We ignore the Dagster internal logging to prevent a single error from being logged per node in the job graph
    ignore_logger("dagster")

    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT")
    TRACES_SAMPLE_RATE = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", 0))

    sentry_logger.info("Setting up Sentry with")
    sentry_logger.info(f"SENTRY_DSN: {SENTRY_DSN}")
    sentry_logger.info(f"SENTRY_ENVIRONMENT: {SENTRY_ENVIRONMENT}")
    sentry_logger.info(f"SENTRY_TRACES_SAMPLE_RATE: {TRACES_SAMPLE_RATE}")

    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=TRACES_SAMPLE_RATE,
            environment=SENTRY_ENVIRONMENT,
            default_integrations=False,
            integrations=[
                AtexitIntegration(),
                DedupeIntegration(),
                StdlibIntegration(),
                ModulesIntegration(),
                ArgvIntegration(),
                LoggingIntegration(),
            ],
        )
