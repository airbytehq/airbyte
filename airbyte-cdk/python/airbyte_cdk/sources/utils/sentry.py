#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import contextlib
import os
from typing import Any
from uuid import uuid4

import sentry_sdk


class AirbyteSentry:
    DSN_ENV_NAME = "SENTRY_DSN"
    MAX_BREADCRUMBS = 30
    TRACES_SAMPLE_RATE = 1.0
    sentry_enabled = False
    source_tag = ""
    run_id = str(uuid4())

    @classmethod
    def init(cls, source_tag=None):
        sentry_dsn = os.environ.get(cls.DSN_ENV_NAME)
        if sentry_dsn:
            cls.sentry_enabled = True
            sentry_sdk.init(
                sentry_dsn,
                max_breadcrumbs=cls.MAX_BREADCRUMBS,
                traces_sample_rate=cls.TRACES_SAMPLE_RATE,
            )
            if source_tag:
                sentry_sdk.set_tag("source", source_tag)
                sentry_sdk.set_tag("run_id", cls.run_id)
                cls.source_tag = source_tag

    def if_enabled(f):
        def wrapper(cls, *args, **kvargs):
            if cls.sentry_enabled:
                return f(cls, *args, **kvargs)

        return wrapper

    def if_enabled_else(return_value):
        def if_enabled(f):
            def wrapper(cls, *args, **kvargs):
                if cls.sentry_enabled:
                    return f(cls, *args, **kvargs)
                else:
                    return return_value

            return wrapper

        return if_enabled

    @classmethod
    @if_enabled
    def set_tag(cls, tag_name: str, value: Any):
        sentry_sdk.set_tag(tag_name, value)

    @classmethod
    @if_enabled
    def add_breadcrumb(cls, message, data=None):
        sentry_sdk.add_breadcrumb(message=message, data=data)

    @classmethod
    @if_enabled
    def set_context(cls, name, data):
        sentry_sdk.set_context(name, data)

    @classmethod
    @if_enabled_else(contextlib.nullcontext())
    def start_transaction(cls, op, name=None):
        return sentry_sdk.start_transaction(op=op, name=f"{cls.source_tag}.{name}")

    @classmethod
    @if_enabled_else(contextlib.nullcontext())
    def start_transaction_span(cls, op, description=None):
        return sentry_sdk.start_span(op=op, description=description)
