from typing import Iterable, TypeVar, Generic
from airbyte_lib.cache import Cache
from airbyte_lib.source import Source
from airbyte_protocol.models import AirbyteRecordMessage, Type
from dataclasses import dataclass

TCache = TypeVar('TCache', bound=Cache)

@dataclass
class SyncResult(Generic[TCache]):
    processed_records: int
    cache: TCache

class Connection(Generic[TCache]):
    """This class is representing a source that can be called"""

    def __init__(
        self,
        source: Source,
        cache: TCache,
    ):
        self.source = source
        self.cache = cache
    
    def _process(self, messages: Iterable[AirbyteRecordMessage]):
        self._processed_records = 0
        for message in messages:
            self._processed_records += 1
            yield message

    def sync(self) -> SyncResult[TCache]:
        self.cache.write(self._process(self.source.read()))

        return SyncResult(
            processed_records=self._processed_records,
            cache=self.cache,
        )
