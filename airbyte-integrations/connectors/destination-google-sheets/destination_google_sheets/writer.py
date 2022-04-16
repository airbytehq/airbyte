#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk import AirbyteLogger
from typing import Mapping
from .client import GoogleSpreadsheetsClient
from .helpers import get_record_values


class GoogleSpreadsheetsWriter:
    
    logger = AirbyteLogger()

    buffered_streams = []
    write_buffer = []
    _headers = []
    flush_interval = 1000

    def __init__(self, client: GoogleSpreadsheetsClient):
        self.client = client
    
    def buffer_stream(self, configured_stream):
        if configured_stream:
            self.write_buffer.append({configured_stream.stream.name: []})
            self._headers.append(
                {
                    configured_stream.stream.name: sorted(list(configured_stream.stream.json_schema.get("properties").keys())),
                    "is_set": False
                }
            )
    
    def add_to_buffer(self, stream_name: str, record: Mapping):   
        for stream in self.write_buffer:
            if stream_name in stream:
                stream[stream_name].append(get_record_values(self.normalize_record(stream_name, record)))
    
    def buffer_has_more_records(self):
        for stream in self.write_buffer:
            stream_name = list(stream.keys())[0]
            if stream_name in stream:
                result = True if len(stream[stream_name]) > 0 else False
        return result
    
    def flush_buffer(self, stream_name: str):
        for stream in self.write_buffer:
            if stream_name in stream:
                stream[stream_name].clear()
    
    def check_headers(self, stream_name: str):     
        for stream in self._headers:
            if stream_name in stream:
                if not stream["is_set"]:
                    self.set_headers(stream_name, stream[stream_name])
                    stream["is_set"] = True
           
    def delete_stream_entries(self, stream_name: str):
        """Deletes all the records belonging to the input stream"""
        self.client.clean_worksheet(f"{stream_name}")
        
    def set_headers(self, stream_name: str, headers_list: list):
        wks = self.client.open_worksheet(f"{stream_name}")
        wks.update_row(1, headers_list)

    def normalize_record(self, stream_name: str, record: Mapping):        
        for stream in self._headers:
            if stream_name in stream:
                for key in stream[stream_name]:
                    if key not in record.keys():
                        record.update({key: ""})
                for key in record.copy().keys():
                    if key not in stream[stream_name]:
                        record.pop(key)

        return dict(sorted(record.items(), key=lambda x: x[0]))
             
    def queue_write_operation(self, stream_name: str):
        for stream in self.write_buffer:
            if stream_name in stream:
                if len(stream[stream_name]) == self.flush_interval:
                    self.write_from_queue(stream_name)
                    self.flush_buffer(stream_name)   
    
    def write_from_queue(self, stream_name: str):
        values = []
        self.check_headers(stream_name)
        for stream in self.write_buffer:
            if stream_name in stream:
                values = stream[stream_name]
        wks = self.client.open_worksheet(f"{stream_name}")
        # TODO:
        print(f"\nValues: {values}\n")
        # 
        if len(values) > 0:
            self.logger.info(f"Writing data for stream: {stream_name}")
            wks.append_table(values, start="A2", dimension='ROWS')
        else:
            self.logger.info(f"Skipping empty stream: {stream_name}")
        
    def write_whats_left(self):
        for stream in self.write_buffer:
            stream_name = list(stream.keys())[0]
            if stream_name in stream:
                self.write_from_queue(stream_name)
                self.flush_buffer(stream_name)
