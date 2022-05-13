#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import abstractmethod
from typing import Tuple

from airbyte_cdk.sources.abstract_source import AbstractSource


class ConfigurableSource(AbstractSource):
    @abstractmethod
    def connection_checker(self):
        pass

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return self.connection_checker().check_connection(logger, config)
