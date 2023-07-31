import os
import sentry_sdk
import functools

from dagster import OpExecutionContext, get_dagster_logger

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

    # TODO explain why?
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
        try:
            log_asset_or_op_context(args[0])
        except (AttributeError, IndexError):
            sentry_logger.warn("Sentry did not find execution context as the first arg")

        try:
            return func(*args, **kwargs)
        except Exception as e:
            event_id = sentry_sdk.capture_exception(e)
            sentry_logger.error(f"Sentry captured an exception. Event ID: {event_id}")
            raise e

    return wrapped_fn

def with_sentry_op_asset_transaction(context: OpExecutionContext):
    sentry_logger.info(f"Initializing Sentry Transaction for Dagster Op/Asset {context.job_name} - {context.op_def.name}")
    return sentry_sdk.start_transaction(
        op=context.op_def.name,
        name=context.job_name,
    )

def start_sentry_transaction(func):
    def wrapped_fn(*args, **kwargs):
        with with_sentry_op_asset_transaction(args[0]):
            return func(*args, **kwargs)

    return wrapped_fn

def ensure_context_arg(func):
    @functools.wraps(func)
    def wrapped_fn(*args, **kwargs):
        if len(args) == 0:
            raise Exception("No context provided to Sentry Transaction. When using @instrument, ensure that the asset/op has a context as the first argument.")
        return func(*args, **kwargs)

    return wrapped_fn

def instrument(func):
    """
    decorate the func with @capture_asset_op_exceptions and @sentry_sdk.trace
    """
    @functools.wraps(func)
    @ensure_context_arg
    @start_sentry_transaction
    @capture_asset_op_exceptions
    def wrapped_fn(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapped_fn
