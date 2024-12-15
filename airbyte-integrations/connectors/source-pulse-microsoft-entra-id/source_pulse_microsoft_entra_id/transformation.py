from typing import Mapping, Any, Iterable, Optional

from jsonref import requests


class TransformationMixin:

    def transform_record(self, record: Mapping[str, Any], stream_slice: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        """
        Transform an individual record.
        By default, returns the record unchanged. Override this method in child classes.
        """
        return record

    def parse_response(self, response: requests.Response, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get("value", [])

        for record in records:
            record = self.transform_record(record, stream_slice=stream_slice)
            yield record
