#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import importlib.metadata
import os
from typing import TYPE_CHECKING

import sentry_sdk
from connector_ops.utils import Connector  # type: ignore

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional

    from asyncclick import Command, Context

    from pipelines.models.steps import Step


def initialize() -> None:
    if "SENTRY_DSN" in os.environ:
        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"),
            environment=os.environ.get("SENTRY_ENVIRONMENT") or "production",
            before_send=before_send,  # type: ignore
            release=f"pipelines@{importlib.metadata.version('pipelines')}",
        )


def before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Ignore logged errors that do not contain an exception
    if "log_record" in hint and "exc_info" not in hint:
        return None

    return event


def with_step_context(func: Callable) -> Callable:
    def wrapper(self: Step, *args: Any, **kwargs: Any) -> Step:
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
                        "support_level": connector.support_level,
                    },
                )

            return func(self, *args, **kwargs)

    return wrapper


def with_command_context(func: Callable) -> Callable:
    def wrapper(self: Command, ctx: Context, *args: Any, **kwargs: Any) -> Command:
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
