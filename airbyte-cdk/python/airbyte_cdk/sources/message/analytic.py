import statistics
import urllib.parse

from datetime import timedelta
from enum import Enum
from itertools import groupby
from typing import Dict, Union, Mapping, Iterable, List


class PaginationMetric(Enum):
    NOT_REPORTED = "NOT_REPORTED"
    REPORTED = "REPORTED"


_MAX_REPORTED_RESPONSES = 1_000_000


class Response:
    def __init__(self, destination: str, status: str, size_in_bytes: int, duration: timedelta, cached: bool):
        self._destination = destination
        self._status = status
        self._size_in_bytes = size_in_bytes
        self._duration = duration
        self._cached = cached

    @property
    def destination(self) -> str:
        return self._destination

    @property
    def status(self) -> str:
        return self._status

    @property
    def duration(self) -> timedelta:
        return self._duration

    @property
    def cached(self) -> bool:
        return self._cached


class StreamMetrics:
    def __init__(self, source_name: str, stream_name: str):
        self._source_name = source_name
        self._stream_name = stream_name
        self._responses = []
        self._metrics: Dict[str, Union[int, str]] = {}
        self._metrics["sync.number_of_records"] = 0
        self._metrics["sync.api.number_of_retries"] = 0

    def on_pagination(self) -> None:
        self._metrics["sync.api.used_pagination"] = PaginationMetric.REPORTED.value

    def on_record(self) -> None:
        self._increment("sync.number_of_records")

    def on_response(self, response: Response) -> None:
        self._responses.append(response)

    def on_retry(self) -> None:
        self._increment("sync.api.number_of_retries")

    def get_report(self):
        from ddtrace import tracer
        span = tracer.current_span()
        if "sync.number_of_records" in self._metrics:
            span.set_tag("sync.number_of_records", self._metrics["sync.number_of_records"])
        if "sync.api.number_of_retries" in self._metrics:
            span.set_tag("sync.api.number_of_retries", self._metrics["sync.api.number_of_retries"])

        return self._metrics | {"responses": self._get_calculated_metrics()} | self._get_metadata()

    def _get_metadata(self) -> Dict[str, str]:
        return {
            "source.name": self._source_name,
            "stream.name": self._stream_name,
        }

    def _get_calculated_metrics(self):
        calculated_metrics = {}
        if not self._responses:
            return calculated_metrics

        for destination, responses in groupby(self._responses, lambda response: response.destination):
            responses = list(responses)
            destination_metrics = dict()

            destination_metrics["duration"] = {}
            durations = list(map(lambda response: response.duration.total_seconds() * 1000, responses))
            duration_in_millis_deciles = self._deciles(durations) if len(durations) > 1 else durations * 9
            destination_metrics["duration"]["median"] = duration_in_millis_deciles[4]
            destination_metrics["duration"]["P90"] = duration_in_millis_deciles[-1]
            destination_metrics["duration"]["average"] = self._average(durations)

            destination_metrics["from_cache"] = self._count(responses, lambda response: response.cached)
            destination_metrics["status"] = {}
            for status, response_for_status in groupby(responses, lambda response: response.status):
                destination_metrics["status"][str(status)] = len(list(response_for_status))

            calculated_metrics[destination] = destination_metrics
        return calculated_metrics

    def _average(self, values: Iterable[Union[int, float]]) -> float:
        return statistics.mean(values)

    def _deciles(self, values: Iterable[Union[int, float]]) -> List[float]:
        return statistics.quantiles(values, n=10)

    def _count(self, values, predicate) -> int:
        return sum(1 for x in values if predicate(x))

    def _increment(self, metric_name: str) -> None:
        if metric_name not in self._metrics:
            self._metrics[metric_name] = 0
        self._metrics[metric_name] += 1
