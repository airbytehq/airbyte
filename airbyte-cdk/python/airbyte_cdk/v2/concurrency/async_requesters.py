#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from typing import AsyncIterator, Generic, Optional, TypeVar

import requests
from airbyte_cdk.v2.concurrency.partition_descriptors import PartitionDescriptor

ClientType = TypeVar("ClientType", bound="RequesterType")
RequestType = TypeVar("RequestType")


class Client(ABC, Generic[RequestType]):
    @abstractmethod
    async def request(self, request: RequestType) -> Optional[requests.Response]:
        pass
