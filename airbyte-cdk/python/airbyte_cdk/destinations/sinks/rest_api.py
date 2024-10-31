# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A sink that sends records to a REST API."""

from typing import Literal

import requests
from typing_extensions import override

from airbyte_cdk import Record
from airbyte_cdk.destinations.sinks.base import StreamSinkBase

HttpWriteMethod = Literal["POST", "PUT", "PATCH", "DELETE"]


class RestSink(StreamSinkBase):
    """A sink that sends records to a REST API."""

    path_template = "{base_url}/{stream_name}/{record[id]}"
    """The template for the URL path to send records to.
    You can use the following placeholders:
    - `{base_url}`: The base URL of the REST API.
    - `{stream_name}`: The name of the stream.
    - `{record[<FIELD_NAME>]}`: A field from the record.
    - `{parent_record[<FIELD_NAME>]}`: A field from the parent stream's record.
    """

    insert_method: HttpWriteMethod = "POST"
    """The HTTP method to use for inserting records. By default, POST is used."""

    update_method: HttpWriteMethod = "PUT"
    """The HTTP method to use for inserting records. By default, PUT is used."""

    def __init__(
        self,
        base_url: str,
        path_template: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.base_url = base_url
        self.path = path_template
        self.records = []

    @override
    def _write_record(self, record: Record) -> None:
        """Write a single record to the sink.

        By default, this method first attempts to update the record in the sink.
        If the record does not exist, it is inserted instead.

        Subclasses can override this method to change how records are written.
        """
        try:
            self._update_record(record)
        except requests.HTTPError as ex:
            # Retry as an insert if the record does not exist.
            if ex.response.status_code == 404:
                self._insert_record(record)

    def _update_record(self, record: Record) -> None:
        """Update a single record that already exists in the sink.

        This method updates the record in the REST API.
        """
        # Send the record to the REST API.
        response: requests.Response = requests.request(
            method=self.update_method,
            url=self.path_template.format(
                base_url=self.base_url,
                stream_name=self.stream_name,
                record=record,
            ),
            json=record,
        )
        response.raise_for_status()

    def _insert_record(self, record: Record) -> None:
        """Insert a single record that does not exist in the sink.

        This method inserts the record into the REST API.
        """
        # Send the record to the REST API.
        response: requests.Response = requests.request(
            method=self.insert_method,
            url=self.path_template.format(
                base_url=self.base_url,
                stream_name=self.stream_name,
                record=record,
            ),
            json=record,
        )
        response.raise_for_status()
