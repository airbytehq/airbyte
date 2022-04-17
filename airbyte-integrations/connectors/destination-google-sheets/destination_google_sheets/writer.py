#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import List
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
        
    def set_headers(self, stream_name: str, headers_list: List[str]):
        """
        Sets headers belonging to the input stream
        """
        wks = self.client.open_worksheet(f"{stream_name}")
        wks.update_row(1, headers_list)
    
    def check_headers(self, stream_name: str):
        """
        Checks whether data headers belonging to the input stream are set.
        """     
        for stream in self.stream_info:
            if stream_name in stream:
                if not stream["is_set"]:
                    self.set_headers(stream_name, stream[stream_name])
                    stream["is_set"] = True
           
    def queue_write_operation(self, stream_name: str):
        """
        Mimics `batch_write` operation using records_buffer.
        
        1) gets data from the records_buffer
        2) writes it to the target worksheet
        3) cleans-up the records_buffer belonging to input stream
        """
        for stream in self.records_buffer:
            if stream_name in stream:
                if len(stream[stream_name]) == self.flush_interval:
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
        for stream in self.records_buffer:
            if stream_name in stream:
                values = stream[stream_name]
        if len(values) > 0:
            wks = self.client.open_worksheet(f"{stream_name}")
            self.logger.info(f"Writing data for stream: {stream_name}")
            wks.append_table(values, start="A2", dimension='ROWS')
        else:
            self.logger.info(f"Skipping empty stream: {stream_name}")
        
    def write_whats_left(self):
        """
        Stands for writing records that are still left to be written,
        but don't match the condition for `queue_write_operation`.
        """
        for stream in self.records_buffer:
            stream_name = list(stream.keys())[0]
            if stream_name in stream:
                self.write_from_queue(stream_name)
                self.flush_buffer(stream_name)
