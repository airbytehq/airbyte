

from typing import Iterable
from airbyte_cdk.models import AirbyteRecordMessage

class InMemoryCache:
    """The in-memory cache is accepting airbyte messages and stores them in a dictionary for streams (one list of dicts per stream)."""

    def __init__(self):
        self.streams = {}
    
    def write(self, messages: Iterable[AirbyteRecordMessage]):
        for message in messages:
            if message.stream not in self.streams:
                self.streams[message.stream] = []
            self.streams[message.stream].append(message.data)

def get_in_memory_cache():
    return InMemoryCache()