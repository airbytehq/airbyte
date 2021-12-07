#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
from typing import Mapping, Any, List, Tuple, Optional

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from recurly import Client, ApiError
from .streams import RecurlyAccountsStream, RecurlyCouponsStream, RecurlyInvoicesStream, \
    RecurlyTransactionsStream, RecurlySubscriptionsStream, RecurlyPlansStream, \
    RecurlyMeasuredUnitsStream, RecurlyExportDatesStream


class SourceRecurly(AbstractSource):
    """
    Recurly API Reference: https://developers.recurly.com/api/v2021-02-25/
    """
    def __init__(self):
        super(SourceRecurly, self).__init__()

        self.__client = None

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            # Checking the API key by trying a test API call to get the first account
            self._client(config).list_accounts().first()
            return True, None
        except ApiError as err:
            return False, err.args[0]

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = self._client(config)

        return [
            RecurlyAccountsStream(client=client),
            RecurlyCouponsStream(client=client),
            RecurlyInvoicesStream(client=client),
            RecurlyMeasuredUnitsStream(client=client),
            RecurlyPlansStream(client=client),
            RecurlySubscriptionsStream(client=client),
            RecurlyTransactionsStream(client=client),
            RecurlyExportDatesStream(client=client)
        ]

    def _client(self, config: json) -> Client:
        if not self.__client:
            self.__client = Client(api_key=config["api_key"])

        return self.__client


