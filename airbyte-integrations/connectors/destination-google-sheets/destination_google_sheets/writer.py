#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import List

from airbyte_cdk.models import AirbyteStream
from pygsheets import Worksheet

from .buffer import WriteBuffer
from .client import GoogleSpreadsheetsClient


class GoogleSpreadsheetsWriter(WriteBuffer):
    def __init__(self, client: GoogleSpreadsheetsClient):
        self.client = client

    def delete_stream_entries(self, stream_name: str):
        """
        Deletes all the records belonging to the input stream.
        """
        self.client.clean_worksheet(f"{stream_name}")
        
    def check_headers(self, stream_name: str):
        """
        Checks whether data headers belonging to the input stream are set.
        """
        for streams in self.stream_info:
            if stream_name in streams:
                if not streams["is_set"]:
                    self.client.set_headers(stream_name, streams[stream_name])
                    streams["is_set"] = True

    def queue_write_operation(self, stream_name: str):
        """
        Mimics `batch_write` operation using records_buffer.

        1) gets data from the records_buffer
        2) writes it to the target worksheet
        3) cleans-up the records_buffer belonging to input stream
        """
        for streams in self.records_buffer:
            if stream_name in streams:
                if len(streams[stream_name]) == self.flush_interval:
                    self.write_from_queue(stream_name)
                    self.flush_buffer(stream_name)

    def write_from_queue(self, stream_name: str):
        """
        Writes data from records_buffer for belonging to the input stream.

        1) checks the headers are set
        2) gets the values from the records_buffer
        3) if there are records to write - writes them to the target worksheet
        """
        values: list = []
        self.check_headers(stream_name)
        
        for streams in self.records_buffer:
            if stream_name in streams:
                values = streams[stream_name]
                
        if len(values) > 0:
            stream: Worksheet = self.client.open_worksheet(f"{stream_name}")
            self.logger.info(f"Writing data for stream: {stream_name}")
            stream.append_table(values, start="A2", dimension="ROWS")
        else:
            self.logger.info(f"Skipping empty stream: {stream_name}")

    def write_whats_left(self):
        """
        Stands for writing records that are still left to be written,
        but don't match the condition for `queue_write_operation`.
        """
        for streams in self.records_buffer:
            stream_name = list(streams.keys())[0]
            if stream_name in streams:
                self.write_from_queue(stream_name)
                self.flush_buffer(stream_name)

    def deduplicate_records(self, configured_stream: AirbyteStream):
        """
        Finds and removes duplicated records for target stream, using `primary_key`.
        Processing the worksheet happens offline and sync it afterwards to reduce API calls rate
        If rate limits are hit while deduplicating, it will be handeled automatically, the operation continues after backoff.
        """
        primary_key: str = configured_stream.primary_key[0][0]
        stream_name: str = configured_stream.stream.name
        
        stream: Worksheet = self.client.open_worksheet(f"{stream_name}")
        rows_to_remove: list = self.client.find_duplicates(stream, primary_key)

        if len(rows_to_remove) > 0:
            self.logger.info(f"Duplicated records are found for stream: {stream_name}, resolving...")
            self.client.remove_duplicates(stream, rows_to_remove)
            self.logger.info(f"Finished deduplicating records for stream: {stream_name}")
        else:
            print(f"No duplicated records found for stream: {stream_name}")
