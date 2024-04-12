import logging
from abc import ABC

from airbyte_cdk.sources.streams.http import HttpStream

logger = logging.getLogger(__name__)


class YandexMetrikaStream(HttpStream, ABC):
    """
    Base for Yandex metrika streams
    Contains some base functions
    """

    def __init__(self, field_name_map: dict[str, str]):
        super().__init__(authenticator=None)
        self.field_name_map: dict[str, str] = field_name_map

    def postprocess_data(self, data: dict[str, any]):
        """Replace keys in data"""
        for old_v, new_v in self.field_name_map.items():
            if old_v in data:
                data[new_v] = data.pop(old_v)

    def replace_keys(self, data: dict[str, any]) -> None:
        """Replace all keys by field_name_map in given dict"""
        for key, value in self.field_name_map.items():
            if key in data:
                data[value] = data.pop(key)
