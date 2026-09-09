# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import hashlib
import json
import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional

import requests
from requests.auth import HTTPBasicAuth

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction
from airbyte_cdk.sources.types import Config, StreamSlice


logger = logging.getLogger("airbyte")


FRESHDESK_EXPORT_DATE_FORMAT = "%d-%m-%Y %H:%M:%S %z"
RFC3339_SECONDS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_EXPORT_UNAVAILABLE_MESSAGE = (
    "Freshdesk ticket activities export is unavailable. Confirm the API key belongs to an "
    "account admin and that the ticket activities scheduled export is enabled."
)


class FreshdeskExportBackoffStrategy(BackoffStrategy):
    """Honor Retry-After when present, otherwise use exponential backoff for 429/5xx."""

    def backoff_time(self, response_or_exception, attempt_count: int) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        return min(2**attempt_count, 60.0)


@dataclass
class TicketActivitiesRetriever(Retriever):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    request_timeout: int = 300
    backoff_strategy: Optional[BackoffStrategy] = field(default=None)
    api_budget: Optional[APIBudget] = field(default=None)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        error_mapping = {
            **DEFAULT_ERROR_MAPPING,
            401: ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.config_error,
                error_message=_EXPORT_UNAVAILABLE_MESSAGE,
            ),
            403: ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.config_error,
                error_message=_EXPORT_UNAVAILABLE_MESSAGE,
            ),
            404: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=None,
                error_message="Freshdesk ticket activities export is not ready yet.",
            ),
        }
        self._http_client = HttpClient(
            name="ticket_activities",
            logger=logger,
            error_handler=HttpStatusErrorHandler(logger, error_mapping=error_mapping),
            api_budget=self.api_budget,
            backoff_strategy=self.backoff_strategy or FreshdeskExportBackoffStrategy(),
        )

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        export_date = self._get_export_date(stream_slice)
        export_payload = self._get_json(
            self._export_endpoint,
            params={"created_at": export_date},
            auth=HTTPBasicAuth(self.config["api_key"], "X"),
            allow_missing=True,
        )
        if not export_payload:
            return

        export_data = export_payload
        if "activities_data" not in export_data:
            download_url = self._extract_download_url(export_payload)
            if not download_url:
                logger.info("No ticket activities export was available for %s", export_date)
                return
            export_data = self._get_json(download_url, allow_missing=True) or {}

        records = export_data.get("activities_data") or []
        if not isinstance(records, list):
            raise AirbyteTracedException(
                message="Freshdesk ticket activities export did not contain an `activities_data` array.",
                failure_type=FailureType.system_error,
            )

        for record in self._add_stable_ids(records, export_date, stream_slice):
            yield record

    @property
    def _export_endpoint(self) -> str:
        return f"https://{self.config['domain']}/api/v2/export/ticket_activities"

    def _get_export_date(self, stream_slice: Optional[StreamSlice]) -> str:
        if stream_slice and stream_slice.get("start_time"):
            raw_date = stream_slice["start_time"]
        else:
            raw_date = self.config.get("start_date") or datetime.now(timezone.utc).strftime(RFC3339_SECONDS_FORMAT)
        return self._parse_datetime(raw_date).date().isoformat()

    def _get_json(
        self,
        url: str,
        params: Optional[Mapping[str, Any]] = None,
        auth: Optional[HTTPBasicAuth] = None,
        allow_missing: bool = False,
    ) -> Optional[Mapping[str, Any]]:
        headers = None
        if auth is not None:
            headers = requests.Request("GET", url, auth=auth).prepare().headers
        _, response = self._http_client.send_request(
            http_method="GET",
            url=url,
            request_kwargs={"timeout": self.request_timeout},
            headers=headers,
            params=params,
        )
        if allow_missing and response.status_code == 404:
            return None
        response.raise_for_status()
        try:
            payload = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise AirbyteTracedException(
                message="Freshdesk ticket activities export returned invalid JSON.",
                failure_type=FailureType.system_error,
            ) from exc
        if not isinstance(payload, Mapping):
            raise AirbyteTracedException(
                message="Freshdesk ticket activities export returned JSON that was not an object.",
                failure_type=FailureType.system_error,
            )
        return payload

    @staticmethod
    def _extract_download_url(payload: Mapping[str, Any]) -> Optional[str]:
        export = payload.get("export")
        if isinstance(export, Mapping) and isinstance(export.get("url"), str):
            return export["url"]
        for key in ("url", "link"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
        return None

    def _add_stable_ids(
        self, records: Iterable[Mapping[str, Any]], export_date: str, stream_slice: Optional[StreamSlice]
    ) -> Iterable[Mapping[str, Any]]:
        seen_record_hashes: dict[str, int] = {}
        for record in records:
            enriched_record = dict(record)
            if "performed_at" not in enriched_record:
                raise AirbyteTracedException(
                    message="Freshdesk ticket activities export record is missing `performed_at`.",
                    failure_type=FailureType.system_error,
                )
            enriched_record["performed_at"] = self._format_datetime(enriched_record["performed_at"])
            if not self._is_in_stream_slice(enriched_record["performed_at"], stream_slice):
                continue
            enriched_record["export_date"] = export_date

            base_hash = self._hash_record(enriched_record)
            seen_record_hashes[base_hash] = seen_record_hashes.get(base_hash, 0) + 1
            enriched_record["_airbyte_ticket_activity_id"] = f"{base_hash}:{seen_record_hashes[base_hash]}"
            yield enriched_record

    @staticmethod
    def _hash_record(record: Mapping[str, Any]) -> str:
        serialized_record = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(serialized_record.encode("utf-8")).hexdigest()

    @classmethod
    def _is_in_stream_slice(cls, performed_at: str, stream_slice: Optional[StreamSlice]) -> bool:
        if stream_slice is None:
            return True
        performed_at_datetime = cls._parse_datetime(performed_at)
        start_time = stream_slice.get("start_time")
        if start_time and performed_at_datetime < cls._parse_datetime(start_time):
            return False
        end_time = stream_slice.get("end_time")
        if end_time and performed_at_datetime > cls._parse_datetime(end_time):
            return False
        return True

    @classmethod
    def _format_datetime(cls, value: Any) -> Any:
        if value in (None, ""):
            return value
        return cls._parse_datetime(value).strftime(RFC3339_SECONDS_FORMAT)

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            parse_value = value
            if parse_value.endswith("Z"):
                parse_value = f"{parse_value[:-1]}+0000"
            for date_format in ("%Y-%m-%dT%H:%M:%S%z", FRESHDESK_EXPORT_DATE_FORMAT, "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(parse_value, date_format)
                    break
                except ValueError:
                    continue
            else:
                raise AirbyteTracedException(
                    message=f"Could not parse Freshdesk ticket activity datetime value `{value}`.",
                    failure_type=FailureType.system_error,
                )
        else:
            raise AirbyteTracedException(
                message=f"Could not parse Freshdesk ticket activity datetime value `{value}`.",
                failure_type=FailureType.system_error,
            )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
