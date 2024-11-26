import sys

from sentry_sdk._compat import contextmanager, reraise
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.crons import capture_checkin
from sentry_sdk.crons.consts import MonitorStatus
from sentry_sdk.utils import now

if TYPE_CHECKING:
    from typing import Generator, Optional


@contextmanager
def monitor(monitor_slug=None):
    # type: (Optional[str]) -> Generator[None, None, None]
    """
    Decorator/context manager to capture checkin events for a monitor.

    Usage (as decorator):
    ```
    import sentry_sdk

    app = Celery()

    @app.task
    @sentry_sdk.monitor(monitor_slug='my-fancy-slug')
    def test(arg):
        print(arg)
    ```

    This does not have to be used with Celery, but if you do use it with celery,
    put the `@sentry_sdk.monitor` decorator below Celery's `@app.task` decorator.

    Usage (as context manager):
    ```
    import sentry_sdk

    def test(arg):
        with sentry_sdk.monitor(monitor_slug='my-fancy-slug'):
            print(arg)
    ```


    """

    start_timestamp = now()
    check_in_id = capture_checkin(
        monitor_slug=monitor_slug, status=MonitorStatus.IN_PROGRESS
    )

    try:
        yield
    except Exception:
        duration_s = now() - start_timestamp
        capture_checkin(
            monitor_slug=monitor_slug,
            check_in_id=check_in_id,
            status=MonitorStatus.ERROR,
            duration=duration_s,
        )
        exc_info = sys.exc_info()
        reraise(*exc_info)

    duration_s = now() - start_timestamp
    capture_checkin(
        monitor_slug=monitor_slug,
        check_in_id=check_in_id,
        status=MonitorStatus.OK,
        duration=duration_s,
    )
