#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import importlib.metadata
import os

import sentry_sdk
from connector_ops.utils import Connector


def initialize():
    if "SENTRY_DSN" in os.environ:
        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"),
            before_send=before_send,
            release=f"pipelines@{importlib.metadata.version('pipelines')}",
        )


def before_send(event, hint):
    # Ignore logged errors that do not contain an exception
    if "log_record" in hint and "exc_info" not in hint:
        return None

    return event


def with_step_context(func):
    def wrapper(self, *args, **kwargs):
        with sentry_sdk.configure_scope() as scope:
            step_name = self.__class__.__name__
            scope.set_tag("pipeline_step", step_name)
            scope.set_context(
                "Pipeline Step",
                {
                    "name": step_name,
                    "step_title": self.title,
                    "max_retries": self.max_retries,
                    "max_duration": self.max_duration,
                    "retry_count": self.retry_count,
                },
            )

            if hasattr(self.context, "connector"):
                connector: Connector = self.context.connector
                scope.set_tag("connector", connector.technical_name)
                scope.set_context(
                    "Connector",
                    {
                        "name": connector.name,
                        "technical_name": connector.technical_name,
                        "language": connector.language,
                        "version": connector.version,
                        "release_stage": connector.release_stage,
                    },
                )

            return func(self, *args, **kwargs)

    return wrapper


def with_command_context(func):
    def wrapper(self, ctx, *args, **kwargs):
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("pipeline_command", self.name)
            scope.set_context(
                "Pipeline Command",
                {
                    "name": self.name,
                    "params": self.params,
                },
            )

            scope.set_context("Click Context", ctx.obj)
            scope.set_tag("git_branch", ctx.obj.get("git_branch", "unknown"))
            scope.set_tag("git_revision", ctx.obj.get("git_revision", "unknown"))

            return func(self, ctx, *args, **kwargs)

    return wrapper
