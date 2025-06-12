#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
import os

import sentry_sdk
from dagster import AssetExecutionContext, OpExecutionContext, SensorEvaluationContext, get_dagster_logger


sentry_logger = get_dagster_logger("sentry")


def setup_dagster_sentry():
    """
    Setup the sentry SDK for Dagster if SENTRY_DSN is defined for the environment.

    Additionally TRACES_SAMPLE_RATE can be set 0-1 otherwise will default to 0.

    Manually sets up a bunch of the default integrations and disables logging of dagster
    to quiet things down.
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


def _is_context(context):
    """
    Check if the given object is a valid context object.
    """
    return (
        isinstance(context, OpExecutionContext)
        or isinstance(context, SensorEvaluationContext)
        or isinstance(context, AssetExecutionContext)
    )


def _get_context_from_args_kwargs(args, kwargs):
    """
    Given args and kwargs from a function call, return the context object if it exists.
    """
    # if the first arg is a context object, return it
    if len(args) > 0 and _is_context(args[0]):
        return args[0]

    # if the kwargs contain a context object, return it
    if "context" in kwargs and _is_context(kwargs["context"]):
        return kwargs["context"]

    # otherwise raise an error
    raise Exception(
        f"No context provided to Sentry Transaction. When using @instrument, ensure that the asset/op has a context as the first argument."
    )


def _with_sentry_op_asset_transaction(context: OpExecutionContext):
    """
    Start or continue a Sentry transaction for the Dagster Op/Asset
    """
    op_name = context.op_def.name
    job_name = context.job_name

    sentry_logger.debug(f"Initializing Sentry Transaction for Dagster Op/Asset {job_name} - {op_name}")
    transaction = sentry_sdk.Hub.current.scope.transaction
    sentry_logger.debug(f"Current Sentry Transaction: {transaction}")
    if transaction:
        return transaction.start_child(
            op=op_name,
        )
    else:
        return sentry_sdk.start_transaction(
            op=op_name,
            name=job_name,
        )


# DECORATORS


def capture_asset_op_context(func):
    """
    Capture Dagster OP context for Sentry Error handling
    """

    @functools.wraps(func)
    def wrapped_fn(*args, **kwargs):
        context = _get_context_from_args_kwargs(args, kwargs)
        with sentry_sdk.configure_scope() as scope:
            scope.set_transaction_name(context.job_name)
            scope.set_tag("job_name", context.job_name)
            scope.set_tag("op_name", context.op_def.name)
            scope.set_tag("run_id", context.run_id)
            scope.set_tag("retry_number", context.retry_number)
            return func(*args, **kwargs)

    return wrapped_fn


def capture_sensor_context(func):
    """
    Capture Dagster Sensor context for Sentry Error handling
    """

    @functools.wraps(func)
    def wrapped_fn(*args, **kwargs):
        context = _get_context_from_args_kwargs(args, kwargs)
        with sentry_sdk.configure_scope() as scope:
            scope.set_transaction_name(context._sensor_name)
            scope.set_tag("sensor_name", context._sensor_name)
            scope.set_tag("run_id", context.cursor)
            return func(*args, **kwargs)

    return wrapped_fn


def capture_exceptions(func):
    """
    Note: This is nessesary as Dagster captures exceptions and logs them before Sentry can.

    Captures exceptions thrown by Dagster Ops and forwards them to Sentry
    before re-throwing them for Dagster.

    Expects ops to receive Dagster context as the first argument,
    but it will continue if it doesn't (it just won't get as much context).

    It will log a unique ID that can be then entered into Sentry to find
    the exception.
    """

    @functools.wraps(func)
    def wrapped_fn(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            event_id = sentry_sdk.capture_exception(e)
            sentry_logger.info(f"Sentry captured an exception. Event ID: {event_id}")
            raise e

    return wrapped_fn


def start_sentry_transaction(func):
    """
    Start a Sentry transaction for the Dagster Op/Asset
    """

    def wrapped_fn(*args, **kwargs):
        context = _get_context_from_args_kwargs(args, kwargs)
        with _with_sentry_op_asset_transaction(context):
            return func(*args, **kwargs)

    return wrapped_fn


def instrument_asset_op(func):
    """
    Instrument a Dagster Op/Asset with Sentry.

    This should be used as a decorator after Dagster's `@op`, or `@asset`
    and the function to be handled.

    This will start a Sentry transaction for the Op/Asset and capture
    any exceptions thrown by the Op/Asset and forward them to Sentry
    before re-throwing them for Dagster.

    This will also send traces to Sentry to help with debugging and performance monitoring.
    """

    @functools.wraps(func)
    @start_sentry_transaction
    @capture_asset_op_context
    @capture_exceptions
    def wrapped_fn(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapped_fn


def instrument_sensor(func):
    """
    Instrument a Dagster Sensor with Sentry.

    This should be used as a decorator after Dagster's `@sensor`
    and the function to be handled.

    This will start a Sentry transaction for the Sensor and capture
    any exceptions thrown by the Sensor and forward them to Sentry
    before re-throwing them for Dagster.

    """

    @functools.wraps(func)
    @capture_sensor_context
    @capture_exceptions
    def wrapped_fn(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapped_fn
