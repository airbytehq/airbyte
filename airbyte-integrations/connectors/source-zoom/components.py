#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
import os
import sqlite3
import time
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from http import HTTPStatus
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Callable, ClassVar, Iterable, Mapping, Optional, Union
from urllib.parse import parse_qs, urlencode, urlsplit

import requests
from requests import HTTPError

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.types import StreamSlice, StreamState


# Zoom Server-to-Server OAuth tokens normally expire in one hour. Refresh
# five minutes early so requests that spend time in the CDK retry/backoff path
# do not cross the token-expiry boundary while still in flight. Zoom's token
# response also includes ``expires_in``; that value is used when available.
BEARER_TOKEN_DEFAULT_EXPIRES_IN = 3600
BEARER_TOKEN_REFRESH_SAFETY_SECONDS = 300



class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


@dataclass
class ServerToServerOauthAuthenticator(NoAuth):
    """Zoom Server-to-Server OAuth with proactive and forced refresh support.

    Tokens are refreshed several minutes before Zoom's advertised expiry. Phone
    requesters can also force a refresh after a 401. ``refresh_after_401`` takes
    the token that was used by the failed request so concurrent workers do not
    all mint a replacement token: only the first worker still holding that stale
    token refreshes; later workers reuse the token it created.
    """

    config: Config
    account_id: Union[InterpolatedString, str]
    client_id: Union[InterpolatedString, str]
    client_secret: Union[InterpolatedString, str]
    authorization_endpoint: Union[InterpolatedString, str]

    _instance = None
    _generate_token_time = 0.0
    _token_refresh_at = 0.0
    _token_expires_at = 0.0
    _access_token = None
    _grant_type = "account_credentials"
    _token_lock: ClassVar[Lock] = Lock()
    _logger: ClassVar[logging.Logger] = logging.getLogger("airbyte.zoom_oauth")

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._account_id = InterpolatedString.create(self.account_id, parameters=parameters).eval(self.config)
        self._client_id = InterpolatedString.create(self.client_id, parameters=parameters).eval(self.config)
        self._client_secret = InterpolatedString.create(self.client_secret, parameters=parameters).eval(self.config)
        self._authorization_endpoint = InterpolatedString.create(self.authorization_endpoint, parameters=parameters).eval(self.config)

    def _needs_refresh(self) -> bool:
        return self._access_token is None or time.time() >= self._token_refresh_at

    def _request_access_token_locked(self, reason: str) -> str:
        token = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode("ascii")).decode("utf-8")
        headers = {"Authorization": f"Basic {token}", "Content-type": "application/json"}
        rest = requests.post(
            url=f"{self._authorization_endpoint}?grant_type={self._grant_type}&account_id={self._account_id}",
            headers=headers,
        )
        if rest.status_code != HTTPStatus.OK:
            raise HTTPError(rest.text)

        payload = rest.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise HTTPError("Zoom OAuth response did not include access_token")

        try:
            expires_in = int(payload.get("expires_in") or BEARER_TOKEN_DEFAULT_EXPIRES_IN)
        except (TypeError, ValueError):
            expires_in = BEARER_TOKEN_DEFAULT_EXPIRES_IN

        now = time.time()
        refresh_after_seconds = max(60, expires_in - BEARER_TOKEN_REFRESH_SAFETY_SECONDS)
        self._access_token = access_token
        self._generate_token_time = now
        self._token_expires_at = now + expires_in
        self._token_refresh_at = now + refresh_after_seconds

        self._logger.info(
            "Zoom OAuth token refreshed "
            f"reason={reason} expires_in={expires_in}s "
            f"refresh_after={refresh_after_seconds}s"
        )
        return access_token

    def ensure_access_token(self) -> str:
        if self._needs_refresh():
            with self._token_lock:
                if self._needs_refresh():
                    try:
                        return self._request_access_token_locked(reason="proactive")
                    except Exception as e:
                        raise Exception(f"Error while generating access token: {e}") from e

        if not self._access_token:
            raise Exception("Error while generating access token: token is empty")
        return self._access_token

    def refresh_after_401(self, stale_token: Optional[str]) -> str:
        """Refresh once for the token that actually received a 401.

        If another worker has already replaced ``stale_token``, return that new
        token instead of generating yet another one.
        """

        with self._token_lock:
            if self._access_token is not None and stale_token is not None and self._access_token != stale_token:
                return self._access_token

            try:
                return self._request_access_token_locked(reason="401")
            except Exception as e:
                raise Exception(f"Error while refreshing access token after 401: {e}") from e

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach a current Zoom bearer token to the outgoing request."""

        access_token = self.ensure_access_token()
        headers = {"Authorization": f"Bearer {access_token}", "Content-type": "application/json"}
        request.headers.update(headers)
        return request

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> Optional[str]:
        return self._access_token if self._access_token else None

    def generate_access_token(self) -> str:
        """Explicitly generate a new token while preserving thread safety."""

        with self._token_lock:
            try:
                return self._request_access_token_locked(reason="explicit")
            except Exception as e:
                raise Exception(f"Error while generating access token: {e}") from e



@dataclass
class ZoomPhoneTranscriptStateMigration(StateMigration):
    """Repair transcript/timeline parent state for incremental parent traversal.

    The child cursor ``recording_date_time`` is copied directly from the
    ``phone_recordings.date_time`` parent record, so it is safe to use as the
    initial parent cursor when upgrading existing state that predates
    ``incremental_dependency: true``.
    """

    _logger: ClassVar[logging.Logger] = logging.getLogger("airbyte.phone_transcript_state")
    _parent_stream_name: ClassVar[str] = "phone_recordings"
    _parent_cursor_field: ClassVar[str] = "date_time"
    _child_cursor_field: ClassVar[str] = "recording_date_time"

    @classmethod
    def _candidate_parent_cursor(cls, stream_state: Mapping[str, Any]) -> tuple[Optional[Any], Optional[str]]:
        parent_state = stream_state.get("parent_state")
        if isinstance(parent_state, Mapping):
            phone_parent_state = parent_state.get(cls._parent_stream_name)
            if isinstance(phone_parent_state, Mapping):
                value = phone_parent_state.get(cls._parent_cursor_field)
                if value not in (None, ""):
                    return value, "parent_state"
                value = phone_parent_state.get(cls._child_cursor_field)
                if value not in (None, ""):
                    return value, "parent_state.recording_date_time"

        legacy_parent_state = stream_state.get(cls._parent_stream_name)
        if isinstance(legacy_parent_state, Mapping):
            value = legacy_parent_state.get(cls._parent_cursor_field)
            if value not in (None, ""):
                return value, "phone_recordings.date_time"
            value = legacy_parent_state.get(cls._child_cursor_field)
            if value not in (None, ""):
                return value, "phone_recordings.recording_date_time"

        global_state = stream_state.get("state")
        if isinstance(global_state, Mapping):
            value = global_state.get(cls._parent_cursor_field)
            if value not in (None, ""):
                return value, "state.date_time"
            value = global_state.get(cls._child_cursor_field)
            if value not in (None, ""):
                return value, "state.recording_date_time"

        value = stream_state.get(cls._parent_cursor_field)
        if value not in (None, ""):
            return value, "date_time"

        value = stream_state.get(cls._child_cursor_field)
        if value not in (None, ""):
            return value, "recording_date_time"

        return None, None

    @classmethod
    def _has_valid_parent_state(cls, stream_state: Mapping[str, Any]) -> bool:
        parent_state = stream_state.get("parent_state")
        if not isinstance(parent_state, Mapping):
            return False
        phone_parent_state = parent_state.get(cls._parent_stream_name)
        return (
            isinstance(phone_parent_state, Mapping)
            and phone_parent_state.get(cls._parent_cursor_field) not in (None, "")
        )

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state or self._has_valid_parent_state(stream_state):
            return False
        cursor_value, _ = self._candidate_parent_cursor(stream_state)
        return cursor_value not in (None, "")

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        cursor_value, source = self._candidate_parent_cursor(stream_state)
        if cursor_value in (None, ""):
            return stream_state

        migrated = dict(stream_state)
        existing_parent_state = migrated.get("parent_state")
        parent_state = dict(existing_parent_state) if isinstance(existing_parent_state, Mapping) else {}
        existing_phone_state = parent_state.get(self._parent_stream_name)
        phone_state = dict(existing_phone_state) if isinstance(existing_phone_state, Mapping) else {}
        phone_state[self._parent_cursor_field] = cursor_value
        parent_state[self._parent_stream_name] = phone_state
        migrated["parent_state"] = parent_state

        self._logger.info(
            "[phone_transcript_state] repaired_parent_state "
            f"parent={self._parent_stream_name} source={source} cursor={cursor_value}"
        )
        return migrated


@dataclass
class TimelineRecordExtractor(RecordExtractor):
    """Extract timeline entries from the cached transcript response."""

    config: Config

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            payload = response.json()
        except (TypeError, ValueError):
            return

        if isinstance(payload, list):
            timeline = payload
        elif isinstance(payload, Mapping):
            timeline = payload.get("timeline")
        else:
            return

        if not isinstance(timeline, list):
            return

        for item in timeline:
            if isinstance(item, Mapping):
                yield dict(item)


@dataclass
class _ZoomPhoneRequestStats:
    """Process-wide request counters shared by concurrent requester instances."""

    started: int = 0
    completed: int = 0
    active: int = 0
    cache_hits: int = 0
    failures: int = 0
    total_duration_ms: int = 0
    last_status: Optional[int] = None
    last_from: Optional[str] = None
    last_to: Optional[str] = None


@dataclass
class ZoomPhoneLoggingRequester(HttpRequester):
    """Zoom Phone requester with concise Airbyte-native INFO progress logging.

    Normal activity is summarized every 200 completed requests. A timer-based
    INFO heartbeat is emitted every 60 seconds while requests are actively in
    flight, including while an HTTP call is stalled. Embedded ``phone_recordings``
    parent traversal also emits an immediate start message. Abnormal HTTP
    responses are logged immediately.
    """

    rate_limit_category: str = "UNKNOWN"
    history_limit_months: Optional[int] = None
    requester_role: str = "default"
    cache_name: Optional[str] = None

    _summary_every: ClassVar[int] = 200
    _heartbeat_interval_seconds: ClassVar[int] = 60
    _request_stats: ClassVar[dict[tuple[str, str], _ZoomPhoneRequestStats]] = {}
    _request_stats_lock: ClassVar[Lock] = Lock()
    _heartbeat_threads: ClassVar[dict[tuple[str, str], Thread]] = {}
    _heartbeat_threads_lock: ClassVar[Lock] = Lock()
    _runtime_version_logged: ClassVar[bool] = False
    _runtime_version_lock: ClassVar[Lock] = Lock()
    _rate_limit_configs_logged: ClassVar[set[tuple[str, str, str]]] = set()
    _rate_limit_config_lock: ClassVar[Lock] = Lock()

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        display_name = self.name
        cache_key = self.cache_name or display_name

        # HttpRequester uses its name only as the native HTTP cache namespace.
        # Temporarily use cache_key while HttpRequester creates its HttpClient,
        # then restore the real stream name for readable logs.
        self.name = cache_key
        try:
            super().__post_init__(parameters)
        finally:
            self.name = display_name

        self._log_runtime_configuration_once()
        self._log_rate_limit_configuration_once()
        self._warn_if_history_window_exceeded()

    @property
    def _stats_key(self) -> tuple[str, str]:
        return self.name, self.requester_role

    def _get_stats(self) -> _ZoomPhoneRequestStats:
        with self._request_stats_lock:
            stats = self._request_stats.get(self._stats_key)
            if stats is None:
                stats = _ZoomPhoneRequestStats()
                self._request_stats[self._stats_key] = stats
            return stats

    @staticmethod
    def _request_dates(response: requests.Response) -> tuple[Optional[str], Optional[str]]:
        request = getattr(response, "request", None)
        url = getattr(request, "url", None)
        if not url:
            return None, None
        query = parse_qs(urlsplit(url).query)
        request_from = query.get("from", [None])[-1]
        request_to = query.get("to", [None])[-1]
        return request_from, request_to

    def _log_summary(self) -> None:
        stats = self._get_stats()
        with self._request_stats_lock:
            started = stats.started
            completed = stats.completed
            active = stats.active
            cache_hits = stats.cache_hits
            failures = stats.failures
            total_duration_ms = stats.total_duration_ms
            last_status = stats.last_status
            last_from = stats.last_from
            last_to = stats.last_to

        avg_ms = round(total_duration_ms / completed) if completed else 0
        cache_rate = (cache_hits / completed) * 100 if completed else 0.0
        fields = [
            f"[{self.name}]",
            f"role={self.requester_role}",
            f"requests={completed}",
            f"started={started}",
            f"active={active}",
            f"avg_ms={avg_ms}",
            f"cache_hits={cache_hits}",
            f"cache={cache_rate:.1f}%",
            f"failures={failures}",
        ]
        if last_status is not None:
            fields.append(f"last_status={last_status}")
        if last_from is not None:
            fields.append(f"last_from={last_from}")
        if last_to is not None:
            fields.append(f"last_to={last_to}")

        self.logger.info(" ".join(fields))

    def _log_parent_start(self) -> None:
        self.logger.info(
            f"[{self.name}] role={self.requester_role} parent_fetch=start"
        )

    @classmethod
    def _heartbeat_loop(
        cls,
        stats_key: tuple[str, str],
        logger: logging.Logger,
        display_name: str,
        requester_role: str,
    ) -> None:
        while True:
            time.sleep(cls._heartbeat_interval_seconds)
            with cls._request_stats_lock:
                stats = cls._request_stats.get(stats_key)
                if stats is None or stats.active <= 0:
                    continue
                started = stats.started
                completed = stats.completed
                active = stats.active
                cache_hits = stats.cache_hits
                failures = stats.failures
                last_status = stats.last_status

            fields = [
                f"[{display_name}]",
                f"role={requester_role}",
                "heartbeat",
                f"active={active}",
                f"started={started}",
                f"completed={completed}",
                f"cache_hits={cache_hits}",
                f"failures={failures}",
            ]
            if last_status is not None:
                fields.append(f"last_status={last_status}")
            logger.info(" ".join(fields))

    def _ensure_heartbeat_thread(self) -> None:
        stats_key = self._stats_key
        with self._heartbeat_threads_lock:
            existing = self._heartbeat_threads.get(stats_key)
            if existing is not None and existing.is_alive():
                return
            thread = Thread(
                target=self._heartbeat_loop,
                args=(stats_key, self.logger, self.name, self.requester_role),
                name=f"airbyte-phone-heartbeat-{self.name}-{self.requester_role}",
                daemon=True,
            )
            self._heartbeat_threads[stats_key] = thread
            thread.start()

    def _get_custom_cached_response(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        path: Optional[str],
        request_params: Optional[Mapping[str, Any]],
    ) -> Optional[requests.Response]:
        return None

    def _store_custom_cached_response(
        self,
        response: requests.Response,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        path: Optional[str],
        request_params: Optional[Mapping[str, Any]],
    ) -> None:
        return None

    def _zoom_oauth_authenticator(self) -> Optional[ServerToServerOauthAuthenticator]:
        authenticator = getattr(self, "authenticator", None)
        if isinstance(authenticator, ServerToServerOauthAuthenticator):
            return authenticator
        return None

    @staticmethod
    def _is_401_auth_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return "401" in message and ("unauthorized" in message or "access token" in message)

    def _send_http_with_auth_retry(
        self,
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        path: Optional[str],
        request_headers: Optional[Mapping[str, Any]],
        request_params: Optional[Mapping[str, Any]],
        request_body_data: Optional[Union[Mapping[str, Any], str]],
        request_body_json: Optional[Mapping[str, Any]],
        log_formatter: Optional[Callable[[requests.Response], Any]],
    ) -> Optional[requests.Response]:
        """Send one logical HTTP request, refreshing/retrying once on 401.

        Airbyte's HttpClient converts a 401 into an AirbyteTracedException before
        HttpRequester returns a Response. Catch it around the HttpRequester call,
        force a Zoom token refresh, and replay the same logical request exactly
        once. Persistent 401s still propagate normally after that single retry.
        """

        authenticator = self._zoom_oauth_authenticator()
        stale_token: Optional[str] = None
        if authenticator is not None:
            # Ensure the token used for this attempt has already passed the
            # proactive-expiry check, and remember it for concurrency-safe 401
            # invalidation. HttpRequester will invoke the authenticator again
            # while preparing the request, but it will reuse this same token.
            stale_token = authenticator.ensure_access_token()

        def _send() -> Optional[requests.Response]:
            return super(ZoomPhoneLoggingRequester, self).send_request(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
                path=path,
                request_headers=request_headers,
                request_params=request_params,
                request_body_data=request_body_data,
                request_body_json=request_body_json,
                log_formatter=log_formatter,
            )

        try:
            return _send()
        except Exception as exc:
            if authenticator is None or not self._is_401_auth_error(exc):
                raise

            authenticator.refresh_after_401(stale_token)
            self.logger.warning(
                f"OAuthRetry [{self.name}] role={self.requester_role} "
                "status=401 token_refreshed=true retry=1/1"
            )
            return _send()

    def send_request(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        stats = self._get_stats()
        with self._request_stats_lock:
            stats.started += 1
            started_count = stats.started
            stats.active += 1

        if self.requester_role == "transcript_parent" and started_count == 1:
            self._log_parent_start()

        self._ensure_heartbeat_thread()

        started_at = time.monotonic()
        try:
            response = self._get_custom_cached_response(
                stream_slice=stream_slice,
                next_page_token=next_page_token,
                path=path,
                request_params=request_params,
            )
            if response is None:
                response = self._send_http_with_auth_retry(
                    stream_state=stream_state,
                    stream_slice=stream_slice,
                    next_page_token=next_page_token,
                    path=path,
                    request_headers=request_headers,
                    request_params=request_params,
                    request_body_data=request_body_data,
                    request_body_json=request_body_json,
                    log_formatter=log_formatter,
                )
                if response is not None:
                    self._store_custom_cached_response(
                        response=response,
                        stream_slice=stream_slice,
                        next_page_token=next_page_token,
                        path=path,
                        request_params=request_params,
                    )
        except Exception as exc:
            duration_ms = round((time.monotonic() - started_at) * 1000)
            with self._request_stats_lock:
                stats.active = max(0, stats.active - 1)
                stats.failures += 1
                stats.total_duration_ms += duration_ms

            self.logger.warning(
                f"Failed [{self.name}] role={self.requester_role} "
                f"category={self.rate_limit_category} duration_ms={duration_ms} "
                f"error={type(exc).__name__}"
            )
            raise

        duration_ms = round((time.monotonic() - started_at) * 1000)
        if response is None:
            with self._request_stats_lock:
                stats.active = max(0, stats.active - 1)
                stats.failures += 1
                stats.total_duration_ms += duration_ms
            self.logger.warning(
                f"Failed [{self.name}] role={self.requester_role} "
                f"category={self.rate_limit_category} duration_ms={duration_ms} response=None"
            )
            return None

        request_from, request_to = self._request_dates(response)
        from_cache = bool(getattr(response, "from_cache", False))
        with self._request_stats_lock:
            stats.completed += 1
            completed_count = stats.completed
            stats.active = max(0, stats.active - 1)
            stats.total_duration_ms += duration_ms
            stats.last_status = response.status_code
            if from_cache:
                stats.cache_hits += 1
            if request_from is not None:
                stats.last_from = request_from
            if request_to is not None:
                stats.last_to = request_to

        if completed_count % self._summary_every == 0:
            self._log_summary()

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS or response.status_code >= 500:
            self.logger.warning(
                f"Response [{self.name}] role={self.requester_role} "
                f"category={self.rate_limit_category} status={response.status_code} "
                f"duration_ms={duration_ms} cache_hit={from_cache}"
            )

        return response

    @staticmethod
    def _months_ago(months: int) -> date:
        today = datetime.now(timezone.utc).date()
        month_index = today.year * 12 + today.month - 1 - months
        year, zero_based_month = divmod(month_index, 12)
        month = zero_based_month + 1
        day = min(today.day, monthrange(year, month)[1])
        return date(year, month, day)

    def _log_runtime_configuration_once(self) -> None:
        if ZoomPhoneLoggingRequester._runtime_version_logged:
            return

        with ZoomPhoneLoggingRequester._runtime_version_lock:
            if ZoomPhoneLoggingRequester._runtime_version_logged:
                return
            try:
                cdk_version = package_version("airbyte-cdk")
            except PackageNotFoundError:
                cdk_version = "unknown"
            configured_workers = self.config.get("num_workers", 20)
            light_rps = self.config.get("phone_light_requests_per_second", 20)
            medium_rps = self.config.get("phone_medium_requests_per_second", 10)
            heavy_rps = self.config.get("phone_heavy_requests_per_second", 5)
            heavy_per_day = self.config.get("phone_heavy_requests_per_day", 15000)
            self.logger.info(
                f"Runtime cdk={cdk_version} workers={configured_workers}"
            )
            self.logger.info(
                "API budget "
                f"light={light_rps}/s "
                f"medium={medium_rps}/s "
                f"heavy={heavy_rps}/s "
                f"heavy_day={heavy_per_day}/day"
            )
            ZoomPhoneLoggingRequester._runtime_version_logged = True

    def _log_rate_limit_configuration_once(self) -> None:
        key = (self.name, self.requester_role, self.rate_limit_category)
        with ZoomPhoneLoggingRequester._rate_limit_config_lock:
            if key in ZoomPhoneLoggingRequester._rate_limit_configs_logged:
                return
            self.logger.info(
                f"RateLimit [{self.name}] role={self.requester_role} category={self.rate_limit_category}"
            )
            ZoomPhoneLoggingRequester._rate_limit_configs_logged.add(key)

    def _warn_if_history_window_exceeded(self) -> None:
        if self.history_limit_months is None:
            return

        configured_start = self.config.get("phone_initial_start_date")
        if not configured_start:
            return

        try:
            requested_start = date.fromisoformat(str(configured_start))
        except (TypeError, ValueError):
            return

        earliest_start = self._months_ago(self.history_limit_months) + timedelta(days=1)
        if requested_start < earliest_start:
            self.logger.warning(
                f"Notice [{self.name}] "
                f"requested_phone_initial_start_date={requested_start.isoformat()} "
                f"exceeds_zoom_history_window={self.history_limit_months}m "
                f"effective_start_date={earliest_start.isoformat()}"
            )


@dataclass
class ZoomPhoneRecordingsRequester(ZoomPhoneLoggingRequester):
    """Disk-cache ``/phone/recordings`` pages for reuse by child traversals.

    Airbyte instantiates the selected ``phone_recordings`` stream and the
    embedded ``phone_recordings`` parent used by transcript streams separately.
    Without an explicit shared cache, those retrievers can call Zoom for the
    same date/page more than once.

    Cache each final HTTP 200 page in a process-local on-disk SQLite database.
    The key is the actual pagination identity: ``from``, ``to``, ``page_size``
    and the *current* ``next_page_token``. The first page uses an empty token.
    Cached responses include Zoom's returned ``next_page_token``, so a later
    traversal follows the exact original pagination chain and does not depend on
    Zoom generating deterministic cursor tokens across separate requests.

    A per-page single-flight lock means that if the selected stream and an
    embedded parent happen to request the same page concurrently, only one of
    them calls Zoom; the other waits briefly and then reads the stored response.
    Different pages/date windows remain fully concurrent, so ``num_workers`` is
    not reduced.
    """

    use_cache: bool = False
    cache_page_size: int = 300

    _cache_lock: ClassVar[Lock] = Lock()
    _cache_connection: ClassVar[Optional[sqlite3.Connection]] = None
    _cache_path: ClassVar[Optional[str]] = None
    _cache_config_logged: ClassVar[bool] = False
    _cache_error_logged: ClassVar[bool] = False
    _first_hit_logged_for_roles: ClassVar[set[tuple[str, str]]] = set()
    _page_locks: ClassVar[dict[tuple[str, str, int, str], Lock]] = {}
    _page_locks_lock: ClassVar[Lock] = Lock()

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        # Do not stack Airbyte's generic requests-cache SQLite backend on top of
        # this cache. This explicit cache is shared by the selected stream and
        # embedded parents and avoids the native cache's concurrent-write
        # ``database is locked`` behaviour seen with many CDK workers.
        self.use_cache = False
        super().__post_init__(parameters)
        self._ensure_recordings_cache()

    @classmethod
    def _recordings_cache_file(cls) -> str:
        if cls._cache_path is None:
            cls._cache_path = os.environ.get(
                "AIRBYTE_ZOOM_PHONE_RECORDINGS_CACHE_PATH",
                f"/tmp/airbyte-zoom-phone-recordings-cache-{os.getpid()}.sqlite",
            )
        return cls._cache_path

    def _ensure_recordings_cache(self) -> None:
        with self._cache_lock:
            if self.__class__._cache_connection is None:
                cache_path = self._recordings_cache_file()
                Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
                connection = sqlite3.connect(cache_path, timeout=30, check_same_thread=False)
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute("PRAGMA synchronous=NORMAL")
                connection.execute("PRAGMA busy_timeout=30000")
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS phone_recordings_page_cache (
                        request_from TEXT NOT NULL,
                        request_to TEXT NOT NULL,
                        page_size INTEGER NOT NULL,
                        page_token TEXT NOT NULL,
                        status_code INTEGER NOT NULL,
                        content BLOB NOT NULL,
                        content_type TEXT,
                        encoding TEXT,
                        PRIMARY KEY (request_from, request_to, page_size, page_token)
                    )
                    """
                )
                connection.commit()
                self.__class__._cache_connection = connection

            if not self.__class__._cache_config_logged:
                self.logger.info(
                    f"Cache [{self.name}] namespace=phone_recordings_pages "
                    f"backend=sqlite key=from,to,page_size,next_page_token "
                    f"path={self._recordings_cache_file()} single_flight=true"
                )
                self.__class__._cache_config_logged = True

    @staticmethod
    def _slice_mapping(stream_slice: Optional[StreamSlice]) -> list[Mapping[str, Any]]:
        mappings: list[Mapping[str, Any]] = []
        if stream_slice is None:
            return mappings

        cursor_slice = getattr(stream_slice, "cursor_slice", None)
        if isinstance(cursor_slice, Mapping):
            mappings.append(cursor_slice)

        partition = getattr(stream_slice, "partition", None)
        if isinstance(partition, Mapping):
            mappings.append(partition)

        if isinstance(stream_slice, Mapping):
            mappings.append(stream_slice)

        return mappings

    @classmethod
    def _window_from_slice(
        cls,
        stream_slice: Optional[StreamSlice],
        request_params: Optional[Mapping[str, Any]],
    ) -> tuple[Optional[str], Optional[str]]:
        if isinstance(request_params, Mapping):
            request_from = request_params.get("from")
            request_to = request_params.get("to")
            if request_from not in (None, "") and request_to not in (None, ""):
                return str(request_from), str(request_to)

        for mapping in cls._slice_mapping(stream_slice):
            request_from = mapping.get("from", mapping.get("start_time"))
            request_to = mapping.get("to", mapping.get("end_time"))
            if request_from not in (None, "") and request_to not in (None, ""):
                return str(request_from), str(request_to)

        return None, None

    @staticmethod
    def _page_token_value(
        next_page_token: Optional[Mapping[str, Any]],
        request_params: Optional[Mapping[str, Any]],
    ) -> str:
        if isinstance(request_params, Mapping):
            value = request_params.get("next_page_token")
            if value not in (None, ""):
                return str(value)

        if isinstance(next_page_token, Mapping):
            value = next_page_token.get("next_page_token")
            if value not in (None, ""):
                return str(value)
            if len(next_page_token) == 1:
                value = next(iter(next_page_token.values()))
                if value not in (None, ""):
                    return str(value)

        return ""

    def _cache_key(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        request_params: Optional[Mapping[str, Any]],
    ) -> Optional[tuple[str, str, int, str]]:
        request_from, request_to = self._window_from_slice(stream_slice, request_params)
        if request_from is None or request_to is None:
            return None
        page_token = self._page_token_value(next_page_token, request_params)
        return request_from, request_to, int(self.cache_page_size), page_token

    @classmethod
    def _single_flight_lock(cls, key: tuple[str, str, int, str]) -> Lock:
        with cls._page_locks_lock:
            lock = cls._page_locks.get(key)
            if lock is None:
                lock = Lock()
                cls._page_locks[key] = lock
            return lock

    @classmethod
    def _log_cache_error_once(cls, logger: logging.Logger, operation: str, exc: Exception) -> None:
        with cls._cache_lock:
            if cls._cache_error_logged:
                return
            logger.warning(
                f"Phone recordings page cache {operation} failed; falling back to Zoom HTTP. "
                f"error={type(exc).__name__}"
            )
            cls._cache_error_logged = True

    def send_request(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        key = self._cache_key(stream_slice, next_page_token, request_params)
        if key is None:
            return super().send_request(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
                path=path,
                request_headers=request_headers,
                request_params=request_params,
                request_body_data=request_body_data,
                request_body_json=request_body_json,
                log_formatter=log_formatter,
            )

        # Hold only the lock for this exact page. Other date windows/pages keep
        # running concurrently. On a concurrent miss, the waiting requester will
        # re-enter the base method after the first requester stores the response
        # and will therefore get a cache hit instead of calling Zoom again.
        with self._single_flight_lock(key):
            return super().send_request(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
                path=path,
                request_headers=request_headers,
                request_params=request_params,
                request_body_data=request_body_data,
                request_body_json=request_body_json,
                log_formatter=log_formatter,
            )

    def _get_custom_cached_response(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        path: Optional[str],
        request_params: Optional[Mapping[str, Any]],
    ) -> Optional[requests.Response]:
        key = self._cache_key(stream_slice, next_page_token, request_params)
        if key is None:
            return None

        try:
            self._ensure_recordings_cache()
            with self._cache_lock:
                connection = self.__class__._cache_connection
                if connection is None:
                    return None
                row = connection.execute(
                    """
                    SELECT status_code, content, content_type, encoding
                    FROM phone_recordings_page_cache
                    WHERE request_from = ?
                      AND request_to = ?
                      AND page_size = ?
                      AND page_token = ?
                    """,
                    key,
                ).fetchone()
        except sqlite3.Error as exc:
            self._log_cache_error_once(self.logger, "read", exc)
            return None

        if row is None:
            return None

        request_from, request_to, page_size, page_token = key
        status_code, content, content_type, encoding = row
        query = {
            "from": request_from,
            "to": request_to,
            "page_size": page_size,
        }
        if page_token:
            query["next_page_token"] = page_token
        request_url = f"https://api.zoom.us/v2/phone/recordings?{urlencode(query)}"

        response = requests.Response()
        response.status_code = int(status_code)
        response._content = bytes(content)
        response.encoding = encoding
        response.url = request_url
        if content_type:
            response.headers["Content-Type"] = content_type
        prepared_request = requests.PreparedRequest()
        prepared_request.prepare(method="GET", url=request_url)
        response.request = prepared_request
        response.from_cache = True

        role_key = (self.name, self.requester_role)
        with self._cache_lock:
            if role_key not in self.__class__._first_hit_logged_for_roles:
                self.logger.info(
                    f"Cache [{self.name}] role={self.requester_role} "
                    "namespace=phone_recordings_pages first_hit=true"
                )
                self.__class__._first_hit_logged_for_roles.add(role_key)

        return response

    def _store_custom_cached_response(
        self,
        response: requests.Response,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        path: Optional[str],
        request_params: Optional[Mapping[str, Any]],
    ) -> None:
        key = self._cache_key(stream_slice, next_page_token, request_params)
        if key is None or response.status_code != HTTPStatus.OK:
            return

        content = response.content
        if not content:
            return

        try:
            self._ensure_recordings_cache()
            with self._cache_lock:
                connection = self.__class__._cache_connection
                if connection is None:
                    return
                connection.execute(
                    """
                    INSERT OR REPLACE INTO phone_recordings_page_cache (
                        request_from, request_to, page_size, page_token,
                        status_code, content, content_type, encoding
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        key[0],
                        key[1],
                        key[2],
                        key[3],
                        int(response.status_code),
                        sqlite3.Binary(content),
                        response.headers.get("Content-Type"),
                        response.encoding,
                    ),
                )
                connection.commit()
        except sqlite3.Error as exc:
            self._log_cache_error_once(self.logger, "write", exc)


@dataclass
class ZoomPhoneTranscriptRequester(ZoomPhoneLoggingRequester):
    """Cache final Zoom transcript JSON by stable recording ID for this job.

    Zoom's ``/phone/recording_transcript/download/{recording_id}`` endpoint
    responds with HTTP 302 before redirecting to the final HTTP 200 JSON payload.
    Generic URL-based HTTP caching is therefore unreliable for reuse between the
    transcript and timeline streams because the redirect/final URL is not the
    stable recording URL we want to share. This requester stores each final 200
    JSON payload in an on-disk SQLite cache keyed by the stable parent
    ``recording_id``. The sibling timeline stream can then reuse the exact
    response without making the transcript-download request to Zoom again.
    """

    use_cache: bool = False

    _cache_lock: ClassVar[Lock] = Lock()
    _cache_connection: ClassVar[Optional[sqlite3.Connection]] = None
    _cache_path: ClassVar[Optional[str]] = None
    _cache_config_logged: ClassVar[bool] = False
    _cache_error_logged: ClassVar[bool] = False
    _first_hit_logged_for_streams: ClassVar[set[str]] = set()

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        # Zoom returns HTTP 302 for the stable transcript-download URL before
        # redirecting to the final HTTP 200 JSON response. Disable the CDK's
        # generic URL cache here and use the on-disk recording_id cache below so
        # transcript and timeline streams reliably reuse the same payload.
        self.use_cache = False
        super().__post_init__(parameters)
        self._ensure_transcript_cache()

    @classmethod
    def _transcript_cache_file(cls) -> str:
        if cls._cache_path is None:
            cls._cache_path = os.environ.get(
                "AIRBYTE_ZOOM_TRANSCRIPT_CACHE_PATH",
                f"/tmp/airbyte-zoom-phone-transcript-cache-{os.getpid()}.sqlite",
            )
        return cls._cache_path

    def _ensure_transcript_cache(self) -> None:
        with self._cache_lock:
            if self.__class__._cache_connection is None:
                cache_path = self._transcript_cache_file()
                Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
                connection = sqlite3.connect(cache_path, timeout=30, check_same_thread=False)
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute("PRAGMA synchronous=NORMAL")
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS transcript_response_cache (
                        recording_id TEXT PRIMARY KEY,
                        status_code INTEGER NOT NULL,
                        content BLOB NOT NULL,
                        content_type TEXT,
                        encoding TEXT
                    )
                    """
                )
                connection.commit()
                self.__class__._cache_connection = connection

            if not self.__class__._cache_config_logged:
                self.logger.info(
                    f"Cache [{self.name}] namespace=phone_transcript_payload "
                    f"backend=sqlite key=recording_id path={self._transcript_cache_file()}"
                )
                self.__class__._cache_config_logged = True

    @staticmethod
    def _recording_id_from_slice(
        stream_slice: Optional[StreamSlice],
        path: Optional[str],
    ) -> Optional[str]:
        if stream_slice is not None:
            partition = getattr(stream_slice, "partition", None)
            if isinstance(partition, Mapping):
                recording_id = partition.get("parent_id")
                if recording_id not in (None, ""):
                    return str(recording_id)

            if isinstance(stream_slice, Mapping):
                recording_id = stream_slice.get("parent_id")
                if recording_id not in (None, ""):
                    return str(recording_id)

        if path:
            marker = "/phone/recording_transcript/download/"
            if marker in path:
                recording_id = path.split(marker, 1)[1].split("?", 1)[0].strip("/")
                if recording_id:
                    return recording_id
        return None

    @classmethod
    def _log_cache_error_once(cls, logger: logging.Logger, operation: str, exc: Exception) -> None:
        with cls._cache_lock:
            if cls._cache_error_logged:
                return
            logger.warning(
                f"Transcript payload cache {operation} failed; falling back to Zoom HTTP. "
                f"error={type(exc).__name__}"
            )
            cls._cache_error_logged = True

    def _get_custom_cached_response(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        path: Optional[str],
        request_params: Optional[Mapping[str, Any]],
    ) -> Optional[requests.Response]:
        recording_id = self._recording_id_from_slice(stream_slice, path)
        if not recording_id:
            return None

        try:
            self._ensure_transcript_cache()
            with self._cache_lock:
                connection = self.__class__._cache_connection
                if connection is None:
                    return None
                row = connection.execute(
                    """
                    SELECT status_code, content, content_type, encoding
                    FROM transcript_response_cache
                    WHERE recording_id = ?
                    """,
                    (recording_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            self._log_cache_error_once(self.logger, "read", exc)
            return None

        if row is None:
            return None

        status_code, content, content_type, encoding = row
        response = requests.Response()
        response.status_code = int(status_code)
        response._content = bytes(content)
        response.encoding = encoding
        response.url = f"https://api.zoom.us/v2/phone/recording_transcript/download/{recording_id}"
        if content_type:
            response.headers["Content-Type"] = content_type
        prepared_request = requests.PreparedRequest()
        prepared_request.prepare(method="GET", url=response.url)
        response.request = prepared_request
        response.from_cache = True

        with self._cache_lock:
            if self.name not in self.__class__._first_hit_logged_for_streams:
                self.logger.info(
                    f"Cache [{self.name}] namespace=phone_transcript_payload first_hit=true"
                )
                self.__class__._first_hit_logged_for_streams.add(self.name)

        return response

    def _store_custom_cached_response(
        self,
        response: requests.Response,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        path: Optional[str],
        request_params: Optional[Mapping[str, Any]],
    ) -> None:
        recording_id = self._recording_id_from_slice(stream_slice, path)
        if not recording_id or response.status_code != HTTPStatus.OK:
            return

        content = response.content
        if not content:
            return

        try:
            self._ensure_transcript_cache()
            with self._cache_lock:
                connection = self.__class__._cache_connection
                if connection is None:
                    return
                connection.execute(
                    """
                    INSERT OR REPLACE INTO transcript_response_cache (
                        recording_id, status_code, content, content_type, encoding
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        recording_id,
                        int(response.status_code),
                        sqlite3.Binary(content),
                        response.headers.get("Content-Type"),
                        response.encoding,
                    ),
                )
                connection.commit()
        except sqlite3.Error as exc:
            self._log_cache_error_once(self.logger, "write", exc)

