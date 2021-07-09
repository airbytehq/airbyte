#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .zuora_auth import ZuoraAuthenticator
from .zuora_client import ZoqlExportClient


class IncrementalZuoraStream(Stream, ABC):

    # Define general primary key
    primary_key = "id"
    # Define cursor filed
    # cursor_field = "createddate"

    def __init__(self, api: ZoqlExportClient):
        self.api = api
        self.cursor = self.api._zuora_object_cursor(self.name)

    # setting limit of the date-slice for the data query job
    @property
    def limit_days(self) -> int:
        return self.api.window_in_days

    # setting checkpoint interval to the limit of date-slice
    state_checkpoint_interval = limit_days  # FIXME: This should be done once the date-slice yield the records

    # Override Stream.get_json_schema to define dynamic schema
    def get_json_schema(self):
        schema = {}
        schema["properties"] = self.api._zuora_object_to_json_schema(self.name)
        return schema

    @property
    def cursor_field(self):
        return self.cursor

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        # if stream_state is missing, we will use the start-date from config for a full refresh
        stream_state = stream_state.get(self.cursor_field) if stream_state else self.api.start_date
        yield from self.api._get_data_with_date_slice("select", self.name, self.cursor_field, stream_state, self.limit_days)


# Dynamically Generate stream classes
class GenerateStreams:
    """
    Use the list of Zuora Objects to produce the stream classes of the format:
    :: Account(IncrementaZuoraStream), Orders(IncrementaZuoraStream), ..., etc.
    """

    def create_stream_class_from_object_name(zuora_objects: List) -> List:
        # Filter non usefull Zuora Objects, link-tables or history-tables, etc
        filter_zuora_objects = ["aquatasklog", "savedquery"]

        # Define the bases
        cls_base = (IncrementalZuoraStream,)
        cls_props = {}

        # Filter objects
        zuora_objects = [obj for obj in zuora_objects if obj not in filter_zuora_objects]
        # Build the streams
        streams = []
        for obj in zuora_objects:
            # List of zuora objects >> stream classes
            streams.append(type(obj, cls_base, cls_props))
        return streams


# Basic Connections Check
class SourceZuora(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the token.
        """

        auth = ZuoraAuthenticator(config["is_sandbox"]).generateToken(config["client_id"], config["client_secret"])
        print(auth)
        if auth.get("status") == 200:
            return True, None
        else:
            return False, auth["status"]

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run.
        """

        auth = ZuoraAuthenticator(config["is_sandbox"]).generateToken(config["client_id"], config["client_secret"])
        args = {
            "authenticator": auth.get("header"),
            "start_date": config["start_date"],
            "window_in_days": config["window_in_days"],
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "is_sandbox": config["is_sandbox"],
        }
        # Making Zuora API Client
        zuora_client = ZoqlExportClient(**args)

        # Get the list of available objects from Zuora
        # zuora_objects = ["account","refund","invoicehistory"]
        zuora_objects = zuora_client._zuora_list_objects()

        # created the class for each object
        streams = GenerateStreams.create_stream_class_from_object_name(zuora_objects)

        # Return the list of stream classes with calling Zuora API Client
        return [ streams[c](zuora_client) for c in range(len(streams)) ]