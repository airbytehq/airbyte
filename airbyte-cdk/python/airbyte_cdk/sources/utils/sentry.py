#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import contextlib
import os
import re
from typing import Any, Callable, List, Optional, Type, Union
from uuid import uuid4

import sentry_sdk
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


class AirbyteSentry:
    """
    Class for working with sentry sdk. It provides methods to:
        - init sentry sdk based on env variable
        - add breadcrumbs and set context
        - work with transactions and transaction spans
        - set tag and capture message and capture exception
    Also it implements client side sensitive data scrubbing.
    """

    DSN_ENV_NAME = "SENTRY_DSN"
    SECRET_MASK = "***"
    # Maximum number of breadcrumbs to send on fail. Breadcrumbs is trail of
    # events that occured before the fail and being sent to server only
    # if handled or unhandled exception occured.
    MAX_BREADCRUMBS = 30
    # Event sending rate. could be from 0 (0%) to 1.0 (100 % events being sent
    # to sentry server)
    TRACES_SAMPLE_RATE = 1.0
    SECRET_REGEXP = [
        re.compile("(api_key=)[a-zA-Z0-9_]+"),
        re.compile("(access_token=)[a-zA-Z0-9_]+"),
        re.compile("(refresh_token=)[a-zA-Z0-9_]+"),
        re.compile("(token )[a-zA-Z0-9_]+"),
        re.compile("(Bearer )[a-zA-Z0-9_]+"),
    ]
    SENSITIVE_KEYS = ["Authorization", "client_secret", "access_token"]

    sentry_enabled = False
    source_tag = ""
    run_id = str(uuid4())
    secret_values: List[str] = []

    @classmethod
    def process_value(cls, key: str, value: str):
        """
        Process single value. Used by recursive replace_value method or
        standalone for single value.
        """
        for secret in cls.secret_values:
            value = value.replace(secret, cls.SECRET_MASK)
        if key in cls.SENSITIVE_KEYS:
            return cls.SECRET_MASK
        for regexp in cls.SECRET_REGEXP:
            value = regexp.sub(f"\\1{cls.SECRET_MASK}", value)
        return value

    @classmethod
    def replace_value(cls, key, value):
        """
        Recursively scan event and replace all sensitive data with SECRET_MASK.
        Perform inplace data replace i.e. its not creating new object.
        """
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = cls.replace_value(k, v)
        elif isinstance(value, list):
            for index, v in enumerate(value):
                value[index] = cls.replace_value(index, v)
        elif isinstance(value, str):
            return cls.process_value(key, value)
        return value

    @classmethod
    def filter_event(cls, event, hint):
        """
        Callback for before_send sentry hook.
        """
        if "message" in event:
            event["message"] = cls.process_value(None, event["message"])
        cls.replace_value(None, event.get("exception"))
        cls.replace_value(None, event.get("contexts"))
        return event

    @classmethod
    def filter_breadcrumb(cls, event, hint):
        """
        Callback for before_breadcrumb sentry hook.
        """
        cls.replace_value(None, event)
        return event

    @classmethod
    def init(
        cls,
        source_tag: str = None,
        transport: Optional[Union[Type[sentry_sdk.transport.Transport], Callable[[Any], None]]] = None,
        secret_values: List[str] = [],
    ):
        """
        Read sentry data source name (DSN) from env variable and initialize sentry cdk.
        Args:
            source_tag: str -  Source name to be used in "source" tag for events organazing.
            transport: Transport or Callable - transport object for transfering
            sentry event to remote server. Usually used for testing, by default
            HTTP transport used
            secret_values: List[str] - list of string that have to be filtered
            out before sending event to sentry server.

        """
        sentry_dsn = os.environ.get(cls.DSN_ENV_NAME)
        if sentry_dsn:
            cls.sentry_enabled = True
            cls.secret_values = secret_values
            sentry_sdk.init(
                sentry_dsn,
                max_breadcrumbs=cls.MAX_BREADCRUMBS,
                traces_sample_rate=cls.TRACES_SAMPLE_RATE,
                before_send=AirbyteSentry.filter_event,
                before_breadcrumb=AirbyteSentry.filter_breadcrumb,
                transport=transport,
                # Use only limited list of integration cause sentry may send
                # transaction events e.g. it could send httplib request with
                # url and authorization info over StdlibIntegration and it
                # would bypass before_send hook.
                integrations=[
                    ExcepthookIntegration(always_run=True),
                    AtexitIntegration(),
                    LoggingIntegration(),
                ],
                # Disable default integrations cause sentry does not allow to
                # filter transactions event that could transfer sensitive data
                default_integrations=False,
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

    # according to issue CDK: typing errors #9500, mypy raises error on this line
    # 'Argument 1 to "if_enabled" has incompatible type "Callable[[Type[AirbyteSentry], str, Any], Any]"; expected "AirbyteSentry"'
    # there are a few similar opened issues
    # https://github.com/python/mypy/issues/12110
    # https://github.com/python/mypy/issues/11619
    # ignored for now
    @classmethod  # type: ignore
    @if_enabled
    def set_tag(cls, tag_name: str, value: Any):
        """
        Set tag that is handy for events organazing and filtering by sentry UI.
        """
        sentry_sdk.set_tag(tag_name, value)

    # same ignored as for line 171
    @classmethod  # type: ignore
    @if_enabled
    def add_breadcrumb(cls, message, data=None):
        """
        Add sentry breadcrumb.
        """
        sentry_sdk.add_breadcrumb(message=message, data=data)

    # same ignored as for line 171
    @classmethod  # type: ignore
    @if_enabled
    def set_context(cls, name, data):
        # Global context being used by transaction event as well. Since we cant
        # filter senstitve data coming from transaction event using sentry
        # before_event hook, apply filter to context here.
        cls.replace_value(None, data)
        sentry_sdk.set_context(name, data)

    # same ignored as for line 171
    @classmethod  # type: ignore
    @if_enabled
    def capture_message(cls, message):
        """
        Send message event to sentry.
        """
        sentry_sdk.capture_message(message)

    # same ignored as for line 171
    @classmethod  # type: ignore
    @if_enabled
    def capture_exception(
        cls,
        error: Optional[BaseException] = None,
        scope: Optional[Any] = None,
        **scope_args,
    ):
        """
        Report handled execption to sentry.
        """
        sentry_sdk.capture_exception(error, scope=scope, **scope_args)

    # same ignored as for line 171
    @classmethod
    @if_enabled_else(contextlib.nullcontext())  # type: ignore
    def start_transaction(cls, op, name=None):
        """
        Return context manager for starting sentry transaction for performance monitoring.
        """
        return sentry_sdk.start_transaction(op=op, name=f"{cls.source_tag}.{name}")

    # same ignored as for line 171
    @classmethod
    @if_enabled_else(contextlib.nullcontext())  # type: ignore
    def start_transaction_span(cls, op, description=None):
        """
        Return context manager for starting sentry transaction span inside existing sentry transaction.
        """
        # Apply filter to description since we cannot use before_send sentry
        # hook for transaction event.
        description = cls.replace_value(None, description)
        return sentry_sdk.start_span(op=op, description=description)
