# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from abc import ABC, abstractmethod


class AbstractFileBasedStreamWriter(ABC):
    def __init__(self) -> None:
        self._config = None
        self._client = None

    @abstractmethod
    def write(self, file_uri: str, fp, file_size: int, logger: logging.Logger):
        """
        Writes a file
        """

    @property
    def client(self):
        return None
