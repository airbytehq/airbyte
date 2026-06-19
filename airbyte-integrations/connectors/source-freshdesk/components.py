# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import hashlib
import json
import logging
from dataclasses import InitVar, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional

import requests
from requests.auth import HTTPBasicAuth

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.types import Config, StreamSlice


logger = logging.getLogger("airbyte")


FRESHDESK_EXPORT_DATE_FORMAT = "%d-%m-%Y %H:%M:%S %z"
RFC3339_SECONDS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass
class TicketActivitiesRetriever(Retriever):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    request_timeout: int = 300

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._session = requests.Session()

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
        response = self._session.get(url, params=params, auth=auth, timeout=self.request_timeout)
        if allow_missing and response.status_code == 404:
            return None
        if response.status_code in (401, 403):
            raise AirbyteTracedException(
                message=(
                    "Freshdesk ticket activities export is unavailable. Confirm the API key belongs to an "
                    "account admin and that the ticket activities scheduled export is enabled."
                ),
                failure_type=FailureType.config_error,
            )
        if response.status_code == 429 or response.status_code >= 500:
            raise AirbyteTracedException(
                message=f"Freshdesk ticket activities export returned HTTP {response.status_code}.",
                failure_type=FailureType.transient_error,
            )
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
