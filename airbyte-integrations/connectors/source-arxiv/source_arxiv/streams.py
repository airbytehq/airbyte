#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs, urlparse

import feedparser
import requests

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.utils import AirbyteTracedException

from .constants import API_PATH, ARXIV_CATEGORIES, BASE_URL, DEFAULT_MAX_RESULTS_PER_PAGE, MAX_RESULTS_PER_PAGE, REQUEST_INTERVAL_SECONDS


logger = logging.getLogger("airbyte")


def _normalize_datetime(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    if value.endswith("Z"):
        return value
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    normalized = _normalize_datetime(value)
    if not normalized:
        return None
    return datetime.fromisoformat(normalized.replace("Z", "+00:00"))


def _max_datetime(left: Optional[str], right: Optional[str]) -> Optional[str]:
    left_datetime = _parse_datetime(left)
    right_datetime = _parse_datetime(right)
    if left_datetime is None:
        return _normalize_datetime(right)
    if right_datetime is None:
        return _normalize_datetime(left)
    return _normalize_datetime(left if left_datetime >= right_datetime else right)


class ArxivStream(HttpStream):
    url_base = f"{BASE_URL}/"
    max_retries = 5
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.search_query = config["search_query"]
        self.start_date = _normalize_datetime(config.get("start_date"))
        self.max_results_per_page = min(int(config.get("max_results_per_page", DEFAULT_MAX_RESULTS_PER_PAGE)), MAX_RESULTS_PER_PAGE)
        self._last_request_at: Optional[float] = None
        self._page_entry_count = 0
        self._total_results: Optional[int] = None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return API_PATH

    def _throttle(self) -> None:
        if self._last_request_at is not None:
            elapsed = time.monotonic() - self._last_request_at
            if elapsed < REQUEST_INTERVAL_SECONDS:
                time.sleep(REQUEST_INTERVAL_SECONDS - elapsed)
        self._last_request_at = time.monotonic()

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        self._throttle()
        return {
            "search_query": self.search_query,
            "start": int(next_page_token.get("start", 0)) if next_page_token else 0,
            "max_results": self.max_results_per_page,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "ascending",
        }

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code == 429 or response.status_code >= 500

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                return None
        return None

    def _parse_feed(self, response: requests.Response):
        raw_xml = response.text
        logger.debug("Raw arXiv XML response: %s", raw_xml)
        parsed = feedparser.parse(raw_xml)
        if parsed.bozo:
            raise AirbyteTracedException(
                message="The arXiv API returned malformed Atom XML.",
                internal_message=str(parsed.bozo_exception),
                failure_type=FailureType.transient_error,
                exception=parsed.bozo_exception,
            )
        feed = parsed.get("feed", {})
        self._page_entry_count = len(parsed.entries)
        try:
            self._total_results = int(feed.get("opensearch_totalresults", 0))
        except (TypeError, ValueError):
            self._total_results = 0
        return parsed

    def _current_start(self, response: requests.Response) -> int:
        request_url = getattr(getattr(response, "request", None), "url", response.url)
        query = parse_qs(urlparse(request_url).query)
        try:
            return int(query.get("start", ["0"])[0])
        except (TypeError, ValueError):
            return 0

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._total_results is None:
            self._parse_feed(response)
        current_start = self._current_start(response)
        next_start = current_start + self.max_results_per_page
        if self._page_entry_count < self.max_results_per_page:
            return None
        if self._total_results is not None and next_start >= self._total_results:
            return None
        return {"start": next_start}


class PapersStream(ArxivStream, IncrementalMixin):
    name = "papers"
    cursor_field = "updated"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, **kwargs)
        self._cursor_value = self.start_date

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value} if self._cursor_value else {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = _normalize_datetime(value.get(self.cursor_field)) if value else self.start_date

    def _starting_cursor(self, stream_state: Mapping[str, Any]) -> Optional[str]:
        stream_state = stream_state or {}
        return _normalize_datetime(stream_state.get(self.cursor_field)) or self._cursor_value or self.start_date

    def _record_from_entry(self, entry: Mapping[str, Any]) -> Mapping[str, Any]:
        entry_id = entry.get("id", "")
        parsed_entry_id = urlparse(entry_id)
        arxiv_id = parsed_entry_id.path.removeprefix("/abs/") if parsed_entry_id.netloc == "arxiv.org" else entry_id
        authors = [author.get("name") for author in entry.get("authors", []) if author.get("name")]
        categories = [tag.get("term") for tag in entry.get("tags", []) if tag.get("term")]
        links = [
            {"href": link.get("href"), "rel": link.get("rel"), "type": link.get("type")}
            for link in entry.get("links", [])
            if link.get("href")
        ]
        return {
            "id": arxiv_id or entry_id,
            "title": " ".join(entry.get("title", "").split()),
            "authors": authors,
            "abstract": " ".join(entry.get("summary", "").split()),
            "published": _normalize_datetime(entry.get("published")),
            "updated": _normalize_datetime(entry.get("updated")),
            "categories": categories,
            "doi": entry.get("arxiv_doi"),
            "journal_ref": entry.get("arxiv_journal_ref"),
            "links": links,
        }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        parsed = self._parse_feed(response)
        current_start = self._current_start(response)
        logger.info("Fetched arXiv papers page starting at %s with %s records", current_start, self._page_entry_count)

        starting_cursor = self._starting_cursor(stream_state)
        starting_cursor_datetime = _parse_datetime(starting_cursor)
        for entry in parsed.entries:
            record = self._record_from_entry(entry)
            updated_datetime = _parse_datetime(record.get(self.cursor_field))
            if starting_cursor_datetime and updated_datetime and updated_datetime <= starting_cursor_datetime:
                continue
            self._cursor_value = _max_datetime(self._cursor_value, record.get(self.cursor_field))
            yield record


class CategoriesStream(Stream):
    name = "categories"
    primary_key = "id"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from ARXIV_CATEGORIES
