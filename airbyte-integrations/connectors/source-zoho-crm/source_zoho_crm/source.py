#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import TYPE_CHECKING, Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource

from .api import ZohoAPI
from .streams import ZohoStreamFactory


if TYPE_CHECKING:
    # This is a workaround to avoid circular import in the future.
    # TYPE_CHECKING is False at runtime, but True when system performs type checking
    # See details here https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
    from airbyte_cdk.sources.streams import Stream


class SourceZohoCrm(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        api = ZohoAPI(config)
        return api.check_connection()

    def streams(self, config: Mapping[str, Any]) -> List["Stream"]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        stream_factory = ZohoStreamFactory(config)
        return stream_factory.produce()
