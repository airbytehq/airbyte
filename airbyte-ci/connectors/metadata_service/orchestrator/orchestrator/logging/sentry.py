import os
import sentry_sdk
import functools

from dagster import OpExecutionContext, get_dagster_logger


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

    ignore_logger("dagster")

    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT")
    TRACES_SAMPLE_RATE = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", 0))

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


def log_asset_or_op_context(context: OpExecutionContext):
    """
    Capture Dagster OP context for Sentry Error handling
    """
    sentry_sdk.add_breadcrumb(
        category="dagster",
        message=f"{context.job_name} - {context.op_def.name}",
        level="info",
        data={
            "run_config": context.run_config,
            "job_name": context.job_name,
            "op_name": context.op_def.name,
            "run_id": context.run_id,
            "retry_number": context.retry_number,
        },
    )

    sentry_sdk.set_tag("job_name", context.job_name)
    sentry_sdk.set_tag("op_name", context.op_def.name)
    sentry_sdk.set_tag("run_id", context.run_id)


def capture_asset_op_exceptions(func):
    """
    Note: This is nessesary as Dagster captures exceptions and logs them before Sentry can.

    Captures exceptions thrown by Dagster Ops and forwards them to Sentry
    before re-throwing them for Dagster.

    Expects ops to receive Dagster context as the first argument,
    but it will continue if it doesn't (it just won't get as much context).

    It will log a unique ID that can be then entered into Sentry to find
    the exception.

    This should be used as a decorator between Dagster's `@op`, or `@asset`
    and the function to be handled.

    @op
    @sentry.capture_asset_op_exceptions
    def op_with_error(context):
        raise Exception("Ahh!")
    """

    @functools.wraps(func)
    def wrapped_fn(*args, **kwargs):
        logger = get_dagster_logger("sentry")

        try:
            log_asset_or_op_context(args[0])
        except (AttributeError, IndexError):
            logger.warn("Sentry did not find execution context as the first arg")

        try:
            return func(*args, **kwargs)
        except Exception as e:
            event_id = sentry_sdk.capture_exception(e)
            logger.error(f"Sentry captured an exception. Event ID: {event_id}")
            raise e

    return wrapped_fn
