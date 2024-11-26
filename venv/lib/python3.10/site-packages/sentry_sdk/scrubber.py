from sentry_sdk.utils import (
    capture_internal_exceptions,
    AnnotatedValue,
    iter_event_frames,
)
from sentry_sdk._compat import string_types
from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from sentry_sdk._types import Event
    from typing import Any
    from typing import Dict
    from typing import List
    from typing import Optional


DEFAULT_DENYLIST = [
    # stolen from relay
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "auth",
    "credentials",
    "mysql_pwd",
    "privatekey",
    "private_key",
    "token",
    "ip_address",
    "session",
    # django
    "csrftoken",
    "sessionid",
    # wsgi
    "remote_addr",
    "x_csrftoken",
    "x_forwarded_for",
    "set_cookie",
    "cookie",
    "authorization",
    "x_api_key",
    "x_forwarded_for",
    "x_real_ip",
    # other common names used in the wild
    "aiohttp_session",  # aiohttp
    "connect.sid",  # Express
    "csrf_token",  # Pyramid
    "csrf",  # (this is a cookie name used in accepted answers on stack overflow)
    "_csrf",  # Express
    "_csrf_token",  # Bottle
    "PHPSESSID",  # PHP
    "_session",  # Sanic
    "symfony",  # Symfony
    "user_session",  # Vue
    "_xsrf",  # Tornado
    "XSRF-TOKEN",  # Angular, Laravel
]


class EventScrubber(object):
    def __init__(self, denylist=None):
        # type: (Optional[List[str]]) -> None
        self.denylist = DEFAULT_DENYLIST if denylist is None else denylist
        self.denylist = [x.lower() for x in self.denylist]

    def scrub_dict(self, d):
        # type: (Dict[str, Any]) -> None
        if not isinstance(d, dict):
            return

        for k in d.keys():
            if isinstance(k, string_types) and k.lower() in self.denylist:
                d[k] = AnnotatedValue.substituted_because_contains_sensitive_data()

    def scrub_request(self, event):
        # type: (Event) -> None
        with capture_internal_exceptions():
            if "request" in event:
                if "headers" in event["request"]:
                    self.scrub_dict(event["request"]["headers"])
                if "cookies" in event["request"]:
                    self.scrub_dict(event["request"]["cookies"])
                if "data" in event["request"]:
                    self.scrub_dict(event["request"]["data"])

    def scrub_extra(self, event):
        # type: (Event) -> None
        with capture_internal_exceptions():
            if "extra" in event:
                self.scrub_dict(event["extra"])

    def scrub_user(self, event):
        # type: (Event) -> None
        with capture_internal_exceptions():
            if "user" in event:
                self.scrub_dict(event["user"])

    def scrub_breadcrumbs(self, event):
        # type: (Event) -> None
        with capture_internal_exceptions():
            if "breadcrumbs" in event:
                if "values" in event["breadcrumbs"]:
                    for value in event["breadcrumbs"]["values"]:
                        if "data" in value:
                            self.scrub_dict(value["data"])

    def scrub_frames(self, event):
        # type: (Event) -> None
        with capture_internal_exceptions():
            for frame in iter_event_frames(event):
                if "vars" in frame:
                    self.scrub_dict(frame["vars"])

    def scrub_spans(self, event):
        # type: (Event) -> None
        with capture_internal_exceptions():
            if "spans" in event:
                for span in event["spans"]:
                    if "data" in span:
                        self.scrub_dict(span["data"])

    def scrub_event(self, event):
        # type: (Event) -> None
        self.scrub_request(event)
        self.scrub_extra(event)
        self.scrub_user(event)
        self.scrub_breadcrumbs(event)
        self.scrub_frames(event)
        self.scrub_spans(event)
