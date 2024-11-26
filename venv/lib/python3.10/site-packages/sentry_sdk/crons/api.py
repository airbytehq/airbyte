import uuid

from sentry_sdk import Hub
from sentry_sdk._types import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any, Dict, Optional


def _create_check_in_event(
    monitor_slug=None,
    check_in_id=None,
    status=None,
    duration_s=None,
    monitor_config=None,
):
    # type: (Optional[str], Optional[str], Optional[str], Optional[float], Optional[Dict[str, Any]]) -> Dict[str, Any]
    options = Hub.current.client.options if Hub.current.client else {}
    check_in_id = check_in_id or uuid.uuid4().hex  # type: str

    check_in = {
        "type": "check_in",
        "monitor_slug": monitor_slug,
        "check_in_id": check_in_id,
        "status": status,
        "duration": duration_s,
        "environment": options.get("environment", None),
        "release": options.get("release", None),
    }

    if monitor_config:
        check_in["monitor_config"] = monitor_config

    return check_in


def capture_checkin(
    monitor_slug=None,
    check_in_id=None,
    status=None,
    duration=None,
    monitor_config=None,
):
    # type: (Optional[str], Optional[str], Optional[str], Optional[float], Optional[Dict[str, Any]]) -> str
    check_in_event = _create_check_in_event(
        monitor_slug=monitor_slug,
        check_in_id=check_in_id,
        status=status,
        duration_s=duration,
        monitor_config=monitor_config,
    )

    hub = Hub.current
    hub.capture_event(check_in_event)

    return check_in_event["check_in_id"]
