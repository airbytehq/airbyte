#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Tuple

from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker


class DeclarativeSource(AbstractSource):
    """
    Base class for declarative Source. Concrete sources need to define the connection_checker to use
    """

    @property
    @abstractmethod
    def connection_checker(self) -> ConnectionChecker:
        """Returns the ConnectioChecker to use for the `check` operation"""

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param logger: The source logger
        :param config: The user-provided configuration as specified by the source's spec.
          This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful
          and we can connect to the underlying data source using the provided configuration.
          Otherwise, the input config cannot be used to connect to the underlying data source,
          and the "error" object should describe what went wrong.
          The error object will be cast to string to display the problem to the user.
        """
        return self.connection_checker.check_connection(self, logger, config)
