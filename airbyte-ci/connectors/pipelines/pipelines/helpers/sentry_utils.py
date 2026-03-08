# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import contextlib
import os
from typing import Generator

import sentry_sdk

from pipelines import main


def turn_off_sentry() -> None:
    sentry_sdk.init(dsn="")


@contextlib.contextmanager
def with_sentry_pipeline_scope(pipeline_name: str) -> Generator[None, None, None]:
    """
    Sets up Sentry scope for a pipeline run.
    This will append context about the pipeline run to all events sent to Sentry within the scope.
    See https://docs.sentry.io/platforms/python/enriching-events/scopes/#local-scopes.
    """
    if os.environ.get("CI") and sentry_sdk.Hub.current.client is not None:
        with sentry_sdk.isolation_scope() as scope:
            scope.set_tag("pipeline_name", pipeline_name)
            scope.set_tag("pull_request", main.is_pr_context())
            scope.set_tag("branch", main.branch_name())
            scope.set_tag("commit_sha", os.environ.get("CI_PIPELINE_COMMIT_SHA"))
            scope.set_tag("pipeline_start_id", os.environ.get("CI_PIPELINE_IID"))
            scope.set_tag("job_url", os.environ.get("CI_JOB_URL", "unknown"))
            yield
    else:
        yield
