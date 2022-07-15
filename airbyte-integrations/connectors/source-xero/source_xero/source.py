#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

import datetime
import logging
from typing import Any, Iterable, Mapping, Optional, Union, Dict

import requests
from airbyte_cdk.sources.streams.http import HttpStream


from abc import ABC
from typing import Any, Iterable, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from urllib.parse import urljoin

from airbyte_cdk.sources.streams.http.exceptions import RequestBodyException

from .streams import *


class SourceXero(AbstractSource):
    headers = {"Dolead-Current-User": "1", "Dolead-User": "1", "User-Agent": "dolead_client/billing"}

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        response = requests.get(url="http://abilling01.prod.dld/monitoring/version", headers=self.headers)
        if response.status_code == 200:
            return True, None
        else:
            return False, f"The API endpoint is unreachable. Please check your API."

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Accounts(),
                DoleadManualJournals(), DoleadIncManualJournals(), DoleadUkManualJournals(), DoleadDdsManualJournals(),
                DoleadJournals(), DoleadIncJournals(), DoleadUkJournals(), DoleadDdsJournals(),
                Contacts(),
                DoleadInvoices(), DoleadIncInvoices(), DoleadUkInvoices(), DoleadDdsInvoices(),
                TrackingCategories(),
                Tenants(),
                DoleadCreditNotes(), DoleadIncCreditNotes(), DoleadUkCreditNotes(), DoleadDdsCreditNotes(),
                DoleadBankTransactions(), DoleadIncBankTransactions(), DoleadUkBankTransactions(), DoleadDdsBankTransactions()]
