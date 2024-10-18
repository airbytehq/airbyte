# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging
import os
from importlib.metadata import version
from typing import Any, Optional

from segment import analytics  # type: ignore

ENABLE_TRACKING = os.getenv("REGRESSION_TEST_DISABLE_TRACKING") is None
DEBUG_SEGMENT = os.getenv("DEBUG_SEGMENT") is not None
EVENT_NAME = "regression_test_start"
CURRENT_VERSION = version(__name__.split(".")[0])


def on_error(error: Exception, items: Any) -> None:
    logging.warning("An error occurred in Segment Tracking", exc_info=error)


# This is not a secret key, it is a public key that is used to identify the Segment project
analytics.write_key = "hnWfMdEtXNKBjvmJ258F72wShsLmcsZ8"
analytics.send = ENABLE_TRACKING
analytics.debug = DEBUG_SEGMENT
analytics.on_error = on_error


def track_usage(
    user_id: Optional[str],
    pytest_options: dict[str, Any],
) -> None:
    if user_id:
        analytics.identify(user_id)
    else:
        user_id = "airbyte-ci"

    # It contains default pytest option and the custom one passed by the user
    analytics.track(
        user_id,
        EVENT_NAME,
        {
            "pytest_options": pytest_options,
            "package_version": CURRENT_VERSION,
        },
    )
