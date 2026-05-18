"""Stream implementations for the ComfyUI Cloud Airbyte source connector."""

from __future__ import annotations

import logging
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream

logger = logging.getLogger("airbyte")


class ComfyUIStream(HttpStream, ABC):
    """Base stream for all ComfyUI Cloud API endpoints."""

    def __init__(self, api_key: str, base_url: str = "https://cloud.comfy.org", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.api_key = api_key
        self._base_url = base_url.rstrip("/")

    @property
    def url_base(self) -> str:
        return self._base_url

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, str]:
        return {"X-API-Key": self.api_key}

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from [response.json()]


class ComfyUIIncrementalStream(ComfyUIStream, ABC):
    """Base for incremental ComfyUI streams with cursor-based state tracking."""

    @property
    def cursor_field(self) -> str:
        raise NotImplementedError("Subclasses must define cursor_field")

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state: MutableMapping[str, Any] = {}

    def _compare_cursor_values(self, a: str, b: str) -> str:
        """Return the greater of two cursor values.

        Handles both Unix-epoch timestamps (numeric strings) and ISO-8601 datetime
        strings.  For ISO strings, lexicographic comparison is correct because the
        format is zero-padded and UTC-sortable.
        """
        try:
            return str(max(float(a), float(b)))
        except (ValueError, TypeError):
            return max(str(a), str(b))

    def _cursor_value(self, record: Mapping[str, Any]) -> Optional[str]:
        value = record.get(self.cursor_field)
        return str(value) if value is not None else None

    def _is_record_newer(self, record: Mapping[str, Any], cursor_value: Optional[str]) -> bool:
        """Return True if the record's cursor value is >= the stored cursor."""
        if cursor_value is None:
            return True
        record_value = self._cursor_value(record)
        if record_value is None:
            return True
        try:
            return float(record_value) >= float(cursor_value)
        except (ValueError, TypeError):
            return str(record_value) >= str(cursor_value)

    def read_records(
        self,
        sync_mode: Any,
        cursor_field: Optional[list[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        cursor_value = (stream_state or {}).get(self.cursor_field)
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            if self._is_record_newer(record, cursor_value):
                self._update_state(record)
                yield record

    def _update_state(self, record: Mapping[str, Any]) -> None:
        record_cursor = self._cursor_value(record)
        if record_cursor is None:
            return
        current = self._state.get(self.cursor_field)
        if current is None:
            self._state[self.cursor_field] = record_cursor
        else:
            self._state[self.cursor_field] = self._compare_cursor_values(current, record_cursor)


# ---------------------------------------------------------------------------
# Stream 1: Jobs (incremental, paginated)
# ---------------------------------------------------------------------------

class JobsStream(ComfyUIIncrementalStream):
    """Fetches generation jobs from GET /api/jobs with offset/limit pagination."""

    primary_key = "id"
    cursor_field = "create_time"
    _page_size = 100

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/api/jobs"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        body = response.json()
        pagination = body.get("pagination", {})
        if pagination.get("has_more", False):
            current_offset = pagination.get("offset", 0)
            limit = pagination.get("limit", self._page_size)
            return {"offset": current_offset + limit}
        return None

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params: MutableMapping[str, Any] = {
            "limit": self._page_size,
            "offset": 0,
            "sort_by": "create_time",
            "sort_order": "asc",
        }
        if next_page_token:
            params["offset"] = next_page_token["offset"]
        return params

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from response.json().get("jobs", [])


# ---------------------------------------------------------------------------
# Stream 2: Job Details (incremental, sub-resource of Jobs)
# ---------------------------------------------------------------------------

class JobDetailsStream(ComfyUIIncrementalStream):
    """Fetches full details for each job via GET /api/jobs/{job_id}.

    Uses JobsStream as the parent to discover job IDs. Inherits the parent's
    incremental cursor so only new jobs are fetched on subsequent syncs.
    """

    primary_key = "id"
    cursor_field = "create_time"

    def __init__(self, parent: JobsStream, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.parent = parent

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        job_id = (stream_slice or {}).get("job_id", "")
        return f"/api/jobs/{job_id}"

    def stream_slices(
        self,
        *,
        sync_mode: Any,
        cursor_field: Optional[list[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_state = stream_state if stream_state else None
        for record in self.parent.read_records(
            sync_mode=sync_mode,
            stream_state=parent_state,
        ):
            yield {"job_id": record["id"], "create_time": record.get("create_time")}

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield response.json()

    def read_records(
        self,
        sync_mode: Any,
        cursor_field: Optional[list[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # Parent already filters by cursor; skip the incremental filter in the
        # base class and just update state for each record.
        for record in HttpStream.read_records(self, sync_mode, cursor_field, stream_slice, stream_state):
            self._update_state(record)
            yield record


# ---------------------------------------------------------------------------
# Stream 3: Assets (incremental, paginated)
# ---------------------------------------------------------------------------

class AssetsStream(ComfyUIIncrementalStream):
    """Fetches user assets from GET /api/assets with offset/limit pagination."""

    primary_key = "id"
    cursor_field = "created_at"
    _page_size = 100

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/api/assets"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        body = response.json()
        if body.get("has_more", False):
            current_offset = body.get("offset", 0)
            limit = body.get("limit", self._page_size)
            return {"offset": current_offset + limit}
        return None

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params: MutableMapping[str, Any] = {
            "limit": self._page_size,
            "offset": 0,
            "sort": "created_at",
            "order": "asc",
        }
        if next_page_token:
            params["offset"] = next_page_token["offset"]
        return params

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from response.json().get("assets", [])


# ---------------------------------------------------------------------------
# Stream 4: Models (full refresh, two-stage: folders then models)
# ---------------------------------------------------------------------------

class ModelsStream(ComfyUIStream):
    """Fetches available models by first listing folders, then models within each.

    Stage 1: GET /api/models → list of folder names
    Stage 2: GET /api/models/{folder} → models in that folder
    """

    primary_key = ["folder", "name"]

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        folder = (stream_slice or {}).get("folder", "")
        return f"/api/models/{folder}"

    def stream_slices(
        self,
        *,
        sync_mode: Any,
        cursor_field: Optional[list[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # Fetch the list of model folders first.
        url = f"{self._base_url}/api/models"
        headers = {"X-API-Key": self.api_key}
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            folders = resp.json()
            if isinstance(folders, list):
                for folder in folders:
                    yield {"folder": folder}
            else:
                logger.warning("Unexpected /api/models response type: %s", type(folders))
        except requests.RequestException as exc:
            logger.error("Failed to fetch model folders: %s", exc)

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        folder = (stream_slice or {}).get("folder", "")
        body = response.json()
        models = body if isinstance(body, list) else body.get("models", [])
        for model in models:
            if isinstance(model, str):
                yield {"folder": folder, "name": model}
            elif isinstance(model, dict):
                yield {**model, "folder": folder}
            else:
                logger.warning("Unexpected model entry type in folder %s: %s", folder, type(model))


# ---------------------------------------------------------------------------
# Stream 5: Nodes (full refresh)
# ---------------------------------------------------------------------------

class NodesStream(ComfyUIStream):
    """Fetches the node type catalog from GET /api/object_info.

    Response is a dict keyed by node name. Each entry is flattened into a record
    with the ``name`` field set explicitly.
    """

    primary_key = "name"

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/api/object_info"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        body = response.json()
        if not isinstance(body, dict):
            logger.warning("Expected dict from /api/object_info, got %s", type(body))
            return
        for node_name, node_info in body.items():
            record = dict(node_info) if isinstance(node_info, dict) else {"data": node_info}
            record["name"] = node_name
            yield record


# ---------------------------------------------------------------------------
# Stream 6: System Stats (full refresh, singleton)
# ---------------------------------------------------------------------------

class SystemStatsStream(ComfyUIStream):
    """Fetches system information from GET /api/system_stats.

    Returns a single record per sync (singleton stream).
    """

    primary_key = None

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/api/system_stats"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield response.json()
